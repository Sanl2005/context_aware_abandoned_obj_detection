class CreateDetectedObjects < ActiveRecord::Migration[8.1]
  def change
    create_table :detected_objects do |t|
      t.string :track_id
      t.string :object_type
      t.float :confidence
      t.text :bbox
      t.datetime :first_seen_at
      t.datetime :last_seen_at
      t.string :status
      t.references :camera_source, null: false, foreign_key: true

      t.timestamps
    end
  end
end
