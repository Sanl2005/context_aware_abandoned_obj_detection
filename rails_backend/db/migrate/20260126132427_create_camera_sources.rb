class CreateCameraSources < ActiveRecord::Migration[8.1]
  def change
    create_table :camera_sources do |t|
      t.string :name
      t.string :location
      t.string :stream_url
      t.boolean :is_active, default:true

      t.timestamps
    end
  end
end
