require "test_helper"

class Api::RiskAssessmentsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get api_risk_assessments_index_url
    assert_response :success
  end

  test "should get show" do
    get api_risk_assessments_show_url
    assert_response :success
  end

  test "should get create" do
    get api_risk_assessments_create_url
    assert_response :success
  end
end
