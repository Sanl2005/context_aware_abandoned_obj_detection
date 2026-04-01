module Api
  class AbandonedObjectsController < ApplicationController
    skip_before_action :authorize_request
    before_action :set_abandoned_object, only: [:show, :make_permanent, :destroy]

    def index
      # Exclude expired
      @objects = AbandonedObject.active.order(detected_at: :desc)
      render json: @objects.map { |obj| format_object(obj) }
    end

    def show
      render json: format_object(@abandoned_object)
    end

    def make_permanent
      if @abandoned_object.update(is_permanent: true, expires_at: nil)
        render json: format_object(@abandoned_object)
      else
        render json: { error: "Failed to make permanent" }, status: :unprocessable_entity
      end
    end

    def destroy
      @abandoned_object.object_image.purge if @abandoned_object.object_image.attached?
      @abandoned_object.person_image.purge if @abandoned_object.person_image.attached?
      @abandoned_object.destroy
      head :no_content
    rescue => e
      Rails.logger.error("Destroy error: #{e.message}")
      render json: { error: e.message }, status: :internal_server_error
    end

    private

    def set_abandoned_object
      @abandoned_object = AbandonedObject.find(params[:id])
    rescue ActiveRecord::RecordNotFound
      render json: { error: "Object not found" }, status: :not_found
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
