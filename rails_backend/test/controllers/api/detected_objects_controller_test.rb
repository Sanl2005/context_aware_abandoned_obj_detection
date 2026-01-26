require "test_helper"

class Api::DetectedObjectsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get api_detected_objects_index_url
    assert_response :success
  end

  test "should get create" do
    get api_detected_objects_create_url
    assert_response :success
  end

  test "should get show" do
    get api_detected_objects_show_url
    assert_response :success
  end
end
