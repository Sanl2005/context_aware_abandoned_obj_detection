require "test_helper"

class Api::AlertsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get api_alerts_index_url
    assert_response :success
  end

  test "should get create" do
    get api_alerts_create_url
    assert_response :success
  end

  test "should get show" do
    get api_alerts_show_url
    assert_response :success
  end
end
