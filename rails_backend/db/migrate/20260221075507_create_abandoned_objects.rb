class CreateAbandonedObjects < ActiveRecord::Migration[8.1]
  def change
    enable_extension 'pgcrypto' unless extension_enabled?('pgcrypto')

    create_table :abandoned_objects, id: :uuid do |t|
      t.string :tracking_id
      t.references :camera_source, null: false, foreign_key: true
      t.string :person_id
      t.string :threat_level
      t.float :abandonment_score
      t.string :location_type
      t.datetime :detected_at
      t.datetime :expires_at
      t.boolean :is_permanent, default: false

      t.timestamps
    end

    add_index :abandoned_objects, :expires_at
    add_index :abandoned_objects, :is_permanent
    add_index :abandoned_objects, :detected_at
  end
end
