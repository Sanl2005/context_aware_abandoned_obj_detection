class AbandonedObjectsChannel < ApplicationCable::Channel
  def subscribed
    stream_from "abandoned_objects_channel"
  end

  def unsubscribed
    # Any cleanup needed when channel is unsubscribed
  end
end
