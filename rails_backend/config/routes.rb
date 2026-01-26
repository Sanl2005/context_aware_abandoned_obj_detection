Rails.application.routes.draw do
  namespace :api do
    resources :camera_sources
    resources :detected_objects, only: [:index, :create, :show]
    resources :alerts, only: [:index, :create, :show]
  end
end

