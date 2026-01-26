module Api
  class CameraSourcesController < ApplicationController
    before_action :set_camera_source, only: [:show, :update, :destroy]

    def index
      render json: CameraSource.order(created_at: :desc)
    end

    def show
      render json: @camera_source
    end

    def create
      camera_source = CameraSource.new(camera_source_params)
      if camera_source.save
        render json: camera_source, status: :created
      else
        render json: { errors: camera_source.errors.full_messages }, status: :unprocessable_entity
      end
    end

    def update
      if @camera_source.update(camera_source_params)
        render json: @camera_source
      else
        render json: { errors: @camera_source.errors.full_messages }, status: :unprocessable_entity
      end
    end

    def destroy
      @camera_source.destroy
      render json: { message: "Camera source deleted" }
    end

    private

    def set_camera_source
      @camera_source = CameraSource.find(params[:id])
    end

    def camera_source_params
      params.require(:camera_source).permit(:name, :location, :stream_url, :is_active)
    end
  end
end
