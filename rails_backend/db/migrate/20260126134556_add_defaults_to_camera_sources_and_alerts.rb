class AddDefaultsToCameraSourcesAndAlerts < ActiveRecord::Migration[8.1]
  def change
    change_column_default :camera_sources, :is_active, from: nil, to: true 
    change_column_default :alerts, :is_sent, from: nil, to: false
  end
end
