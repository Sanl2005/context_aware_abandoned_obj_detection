class AddContextToCameraSources < ActiveRecord::Migration[8.1]
  def change
    add_column :camera_sources, :location_type, :string
    add_column :camera_sources, :risk_profile_config, :jsonb
  end
end
