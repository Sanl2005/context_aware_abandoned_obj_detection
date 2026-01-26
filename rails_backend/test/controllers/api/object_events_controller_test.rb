require "test_helper"

class Api::ObjectEventsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get api_object_events_index_url
    assert_response :success
  end

  test "should get show" do
    get api_object_events_show_url
    assert_response :success
  end

  test "should get create" do
    get api_object_events_create_url
    assert_response :success
  end
end
