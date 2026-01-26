class CreateObjectEvents < ActiveRecord::Migration[8.1]
  def change
    create_table :object_events do |t|
      t.references :detected_object, null: false, foreign_key: true
      t.string :event_type
      t.text :details
      t.datetime :occurred_at

      t.timestamps
    end
  end
end
