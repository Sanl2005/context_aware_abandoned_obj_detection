class CreateRiskAssessments < ActiveRecord::Migration[8.1]
  def change
    create_table :risk_assessments do |t|
      t.references :detected_object, null: false, foreign_key: true
      t.float :risk_score
      t.string :risk_level
      t.text :reason
      t.datetime :assessed_at

      t.timestamps
    end
  end
end
