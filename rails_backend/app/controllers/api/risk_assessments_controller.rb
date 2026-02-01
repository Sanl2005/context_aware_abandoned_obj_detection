module Api
  class RiskAssessmentsController < ApplicationController
    skip_before_action :authorize_request, only: [:index, :show]
    def index
      render json: RiskAssessment.order(created_at: :desc)
    end

    def show
      render json: RiskAssessment.find(params[:id])
    end

    def create
      risk = RiskAssessment.create!(risk_params)
      render json: risk, status: :created
    end

    private

    def risk_params
      params.require(:risk_assessment).permit(:detected_object_id, :risk_score, :risk_level, :reason, :assessed_at)
    end
  end
end
