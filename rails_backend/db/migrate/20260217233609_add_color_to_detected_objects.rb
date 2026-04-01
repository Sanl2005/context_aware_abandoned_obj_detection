class AddColorToDetectedObjects < ActiveRecord::Migration[8.1]
  def change
    add_column :detected_objects, :color, :string
  end
end
