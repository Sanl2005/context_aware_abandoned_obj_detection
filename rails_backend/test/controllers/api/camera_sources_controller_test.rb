require "test_helper"

class Api::CameraSourcesControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get api_camera_sources_index_url
    assert_response :success
  end

  test "should get create" do
    get api_camera_sources_create_url
    assert_response :success
  end

  test "should get show" do
    get api_camera_sources_show_url
    assert_response :success
  end

  test "should get update" do
    get api_camera_sources_update_url
    assert_response :success
  end

  test "should get destroy" do
    get api_camera_sources_destroy_url
    assert_response :success
  end
end
