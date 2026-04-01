module Api
  class MlResultsController < ApplicationController
    skip_before_action :authorize_request, only: [:create]

    def create
      # Parse payload
      payload = params.permit!
      
      camera_id = payload[:camera_id]
      objects = payload[:objects]
      location_type = payload[:location_type]
      crowd_density = payload[:crowd_density]
      
      camera = CameraSource.find_or_create_by(id: camera_id) do |c|
        c.name = "ML Feed #{camera_id}"
        c.location = "Auto Generated"
        c.stream_url = "http://localhost:5000/video_feed"
      end
      
      # Update Camera Context
      camera.update(location_type: location_type) if location_type.present?
      
      processed_objects = []
      
      objects.each do |obj_data|
        track_id = obj_data[:object_id] # This is the UUID from ML
        
        # Find or Initialize Object
        detected_object = DetectedObject.find_or_initialize_by(track_id: track_id, camera_source: camera)
        
        # Update Attributes
        detected_object.assign_attributes(
          object_type: obj_data[:class_name],
          bbox: obj_data[:bbox].to_s,
          confidence: obj_data[:confidence],
          state: obj_data[:state],
          threat_level: obj_data[:threat_level],
          last_seen_at: Time.current
        )
        
        # Set first_seen if new
        detected_object.first_seen_at ||= Time.current
        
        if detected_object.save
          processed_objects << detected_object
          
          # Check for Alert Condition
          if detected_object.confidence > 0.8 && !detected_object.alerts.where(is_sent: true).exists?
            create_alert(detected_object)
          end
          
          # ------------------------------------------------------------------
          # Create Persistent AbandonedObject for frontend history API
          # ------------------------------------------------------------------
          if obj_data[:is_alert] || obj_data[:confidence].to_f > 0.8
            abandoned_obj = AbandonedObject.find_or_initialize_by(tracking_id: track_id)
            is_new = abandoned_obj.new_record?

            abandoned_obj.camera_source = camera
            abandoned_obj.person_id = obj_data[:owner_id] || obj_data[:person_id]
            abandoned_obj.object_type = obj_data[:class_name]
            abandoned_obj.threat_level = obj_data[:threat_level]
            abandoned_obj.abandonment_score = obj_data[:confidence].to_f
            abandoned_obj.location_type = location_type
            abandoned_obj.detected_at ||= Time.current
            
            # 12 hours expiry unless permanent
            abandoned_obj.expires_at ||= abandoned_obj.detected_at + 12.hours
            abandoned_obj.is_permanent = false if abandoned_obj.is_permanent.nil?
            
            if abandoned_obj.save
              if obj_data[:object_image_base64].present? && !abandoned_obj.object_image.attached?
                attach_base64_image(abandoned_obj, :object_image, obj_data[:object_image_base64], "object_#{track_id}")
              end

              if obj_data[:person_image_base64].present? && !abandoned_obj.person_image.attached?
                attach_base64_image(abandoned_obj, :person_image, obj_data[:person_image_base64], "person_#{track_id}")
              end

              if is_new
                # Broadcast using format_object so image URLs are included
                ActionCable.server.broadcast("abandoned_objects_channel", { type: "NEW_ABANDONED_OBJECT", object: format_object(abandoned_obj) })
              end
            end
          end
          
        else
          Rails.logger.error("Failed to save object #{track_id}: #{detected_object.errors.full_messages}")
        end
      end
      
      render json: { status: "success", processed_count: processed_objects.count }
    end
    
    private
    
    def attach_base64_image(record, attachment_name, base64_data, filename)
      return if base64_data.blank?
      
      Rails.logger.info("[ML_RESULTS] Attaching #{attachment_name} to #{record.class} #{record.id}")
      
      begin
        # Decode standard base64 or Data URI format
        match = base64_data.match(/\Adata:(?<content_type>[-\w]+\/[-\w\+\.]+)?;base64,(?<data>.*)/) || {}
        content_type = match[:content_type] || "image/jpeg"
        data = match[:data] || base64_data
        
        decoded_data = Base64.decode64(data)
        
        record.send(attachment_name).attach(
          io: StringIO.new(decoded_data),
          filename: "#{filename}.jpg",
          content_type: content_type
        )
        
        Rails.logger.info("[ML_RESULTS] Successfully attached #{attachment_name} to #{record.id}")
      rescue => e
        Rails.logger.error("[ML_RESULTS] Failed to attach #{attachment_name} to #{record.id}: #{e.message}")
        Rails.logger.error(e.backtrace.join("\n"))
      end
    end
    
    def create_alert(object)
      alert = Alert.create(
        detected_object: object,
        severity: object.threat_level == "HIGH_RISK" ? "CRITICAL" : "WARNING",
        message: "Abandonment detected: #{object.object_type} at #{object.camera_source.name} (Conf: #{object.confidence.round(2)})",
        is_sent: false
      )
      
      ActionCable.server.broadcast("alerts_channel", {
        type: "NEW_ALERT",
        alert: alert.as_json(include: { detected_object: { include: :camera_source } })
      })
    end

    def create_priority_alert(object, msg)
       Alert.create(
        detected_object: object,
        severity: "CRITICAL",
        message: "#{msg} - #{object.object_type}",
        is_sent: false
      )
    end

    def format_object(obj)
      {
        id: obj.id,
        tracking_id: obj.tracking_id,
        object_type: obj.object_type,
        person_id: obj.person_id,
        threat_level: obj.threat_level,
        abandonment_score: obj.abandonment_score,
        location_type: obj.location_type,
        detected_at: obj.detected_at,
        expires_at: obj.expires_at,
        is_permanent: obj.is_permanent,
        object_image_url: obj.object_image.attached? ? rails_blob_path(obj.object_image, disposition: "inline") : nil,
        person_image_url: obj.person_image.attached? ? rails_blob_path(obj.person_image, disposition: "inline") : nil
      }
    end
  end
end
