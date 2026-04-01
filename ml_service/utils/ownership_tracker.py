"""
Object Ownership Tracker

Tracks person-object relationships based on proximity and assigns ownership.
Used to improve abandonment detection by considering owner distance.
"""

import math
import time


class OwnershipTracker:
    """
    Manages ownership mapping between persons and objects.
    
    Uses proximity-based assignment with hysteresis to prevent rapid ownership changes.
    """
    
    def __init__(self,
                 initial_assignment_distance=10.0,
                 reassignment_distance=5.0,
                 owner_far_threshold=3.0):
        """
        Initialize ownership tracker.
        
        Args:
            initial_assignment_distance: Max distance for initial owner assignment (meters)
            reassignment_distance: Max distance for reassigning to new owner (meters)
            owner_far_threshold: Distance at which owner is considered "far" (meters)
        """
        self.initial_assignment_distance = initial_assignment_distance
        self.reassignment_distance = reassignment_distance
        self.owner_far_threshold = owner_far_threshold
        self.last_update_time = time.time()
        
    def calculate_distance(self, bbox1, bbox2, frame_width=1280, frame_height=720):
        """
        Calculate approximate distance between two bounding boxes.
        
        Args:
            bbox1: [x, y, w, h] first bounding box
            bbox2: [x, y, w, h] second bounding box
            frame_width: Frame width for normalization
            frame_height: Frame height for normalization
            
        Returns:
            Approximate distance in meters
        """
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Get centers
        center1_x = x1 + w1 / 2
        center1_y = y1 + h1 / 2
        center2_x = x2 + w2 / 2
        center2_y = y2 + h2 / 2
        
        # Normalize by frame size
        norm_x1 = center1_x / frame_width
        norm_y1 = center1_y / frame_height
        norm_x2 = center2_x / frame_width
        norm_y2 = center2_y / frame_height
        
        # Euclidean distance in normalized space
        distance_norm = math.sqrt(
            (norm_x1 - norm_x2) ** 2 + 
            (norm_y1 - norm_y2) ** 2
        )
        
        # Convert to approximate meters
        # Rough approximation: assume frame covers ~10m width at typical distance
        distance_meters = distance_norm * 10.0
        
        return distance_meters
    
    def find_closest_person(self, object_bbox, persons):
        """
        Find the closest person to an object.
        
        Args:
            object_bbox: Object bounding box [x, y, w, h]
            persons: List of person TrackedObjects
            
        Returns:
            Tuple of (closest_person_id, distance) or (None, float('inf'))
        """
        if not persons:
            return None, float('inf')
        
        closest_person = None
        min_distance = float('inf')
        
        for person in persons:
            distance = self.calculate_distance(object_bbox, person.bbox)
            
            if distance < min_distance:
                min_distance = distance
                closest_person = person
        
        return closest_person.id if closest_person else None, min_distance
    
    def update_ownership(self, persons, objects):
        """
        Update ownership for all objects based on current person positions.
        
        Args:
            persons: List of TrackedObject instances with class_name == 'person'
            objects: List of TrackedObject instances (non-person objects)
        """
        current_time = time.time()
        # Calculate time delta for absence tracking
        dt = min(current_time - self.last_update_time, 1.0)
        self.last_update_time = current_time
        
        for obj in objects:
            # Skip persons
            if obj.class_name == 'person':
                continue
            
            # Find closest person
            closest_person_id, closest_distance = self.find_closest_person(
                obj.bbox, persons
            )
            
            # Update ownership
            if obj.owner_id is None:
                # No owner assigned yet
                if closest_distance <= self.initial_assignment_distance:
                    obj.owner_id = closest_person_id
                    obj.owner_assigned_at = current_time
                    obj.owner_distance = closest_distance
                else:
                    # No one close enough to assign
                    obj.owner_distance = float('inf')
            else:
                # Owner already assigned
                # Calculate distance to current owner
                current_owner_person = next(
                    (p for p in persons if p.id == obj.owner_id), 
                    None
                )
                
                if current_owner_person:
                    owner_distance = self.calculate_distance(
                        obj.bbox, 
                        current_owner_person.bbox
                    )
                    obj.owner_distance = owner_distance
                    
                    # Check for reassignment
                    # Only reassign if current owner is far AND new person is very close
                    if (owner_distance > self.owner_far_threshold and 
                        closest_distance < self.reassignment_distance):
                        # Reassign to new person
                        obj.owner_id = closest_person_id
                        obj.owner_assigned_at = current_time
                        obj.owner_distance = closest_distance
                else:
                    # Current owner not in frame
                    obj.owner_distance = float('inf')
                    
                    # Assign to new person if one is nearby
                    if closest_distance <= self.reassignment_distance:
                        obj.owner_id = closest_person_id
                        obj.owner_assigned_at = current_time
                        obj.owner_distance = closest_distance

            # Update Owner Absence Time
            # Increment if owner is far away or lost (inf), reset if close (interaction)
            if obj.owner_id:
                if obj.owner_distance > self.owner_far_threshold:
                    obj.owner_absence_time += dt
                else:
                    # Owner is close enough to be considered interacting/supervising
                    obj.owner_absence_time = 0.0
            else:
                # No owner assigned -> Object is alone/unattended
                obj.owner_absence_time += dt
    
    def get_ownership_score(self, owner_distance, ownership_duration):
        """
        Calculate ownership score for abandonment detection.
        
        Args:
            owner_distance: Distance to owner in meters
            ownership_duration: How long object has been owned (seconds)
            
        Returns:
            Score from 0.0 (owner nearby) to 1.0 (abandoned/no owner)
        """
        if owner_distance == float('inf'):
            # No owner
            return 1.0
        
        if owner_distance < 2.0:
            # Owner very close
            base_score = 0.0
        elif owner_distance < 5.0:
            # Owner moderate distance
            base_score = 0.5
        else:
            # Owner far away
            base_score = 1.0
        
        # Increase score if owner has been assigned for a long time
        # (indicates object is normally supervised)
        if ownership_duration > 60:  # 1 minute
            base_score *= 1.2
        
        # Cap at 1.0
        return min(base_score, 1.0)
