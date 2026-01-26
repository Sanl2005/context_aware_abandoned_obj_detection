class CreateAlerts < ActiveRecord::Migration[8.1]
  def change
    create_table :alerts do |t|
      t.references :detected_object, null: false, foreign_key: true
      t.text :message
      t.string :severity
      t.boolean :is_sent, default:false
      t.datetime :sent_at

      t.timestamps
    end
  end
end
