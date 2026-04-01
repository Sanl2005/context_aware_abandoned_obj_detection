class AddObjectTypeToAbandonedObjects < ActiveRecord::Migration[8.1]
  def change
    add_column :abandoned_objects, :object_type, :string
  end
end
