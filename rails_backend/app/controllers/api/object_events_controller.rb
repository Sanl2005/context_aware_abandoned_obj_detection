module Api
  class ObjectEventsController < ApplicationController
    def index
      render json: ObjectEvent.order(created_at: :desc)
    end

    def show
      render json: ObjectEvent.find(params[:id])
    end

    def create
      event = ObjectEvent.create!(object_event_params)
      render json: event, status: :created
    end

    private

    def object_event_params
      params.require(:object_event).permit(:detected_object_id, :event_type, :details, :occurred_at)
    end
  end
end
