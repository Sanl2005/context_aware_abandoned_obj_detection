class Api::AuthController < ApplicationController
    skip_before_action :authorize_request, only: [:login]
    def login
    user = User.find_by(email: params[:email])

    if user&.authenticate(params[:password])
      token = JsonWebToken.encode(user_id: user.id, role: user.role)

      render json: {
        token: token,
        user: { id: user.id, name: user.name, email: user.email, role: user.role }
      }, status: :ok
    else
      render json: { error: "Invalid email or password" }, status: :unauthorized
    end
  end
end
