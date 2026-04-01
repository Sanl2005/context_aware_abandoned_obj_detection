class CleanupAbandonedObjectsJob < ApplicationJob
  queue_as :default

  def perform
    # Destroy all expired objects
    # Note: Using destroy_all instead of delete_all to ensure callbacks (like deleting ActiveStorage images) are run!
    expired_objects = AbandonedObject.where("expires_at <= ? AND is_permanent = ?", Time.current, false)
    
    count = expired_objects.count
    expired_objects.destroy_all

    Rails.logger.info("Cleaned up #{count} expired abandoned objects.")
  end
end
