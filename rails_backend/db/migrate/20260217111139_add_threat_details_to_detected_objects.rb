class AddThreatDetailsToDetectedObjects < ActiveRecord::Migration[8.1]
  def change
    add_column :detected_objects, :threat_level, :string
    add_column :detected_objects, :risk_level, :string
    add_column :detected_objects, :owner_id, :integer
    add_column :detected_objects, :state, :string
  end
end
