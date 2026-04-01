Rails.application.routes.draw do
  namespace :api do
    post "login", to: "auth#login"

    get "risk_assessments/index"
    get "risk_assessments/show"
    get "risk_assessments/create"
    get "object_events/index"
    get "object_events/show"
    get "object_events/create"
    resources :camera_sources
    resources :detected_objects, only: [:index, :create, :show]
    resources :alerts, only: [:index, :create, :show]
    resources :object_events, only: [:index, :show, :create]
    resources :risk_assessments, only: [:index, :show, :create]
    post "ml_results", to: "ml_results#create"

    resources :abandoned_objects, only: [:index, :show, :destroy] do
      member do
        patch :make_permanent
      end
    end
  end
end

