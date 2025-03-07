# protocols.py
class Protocols:
    class Response:
        PLAYER_DATA = "protocol.player_data"
        BALL_DATA = "protocol.ball_data"
        GAME_START = "protocol.game_start"
        GAME_END = "protocol.game_end"
        OPPONENT_LEFT = "protocol.opponent_left"

    class Request:
        PLAYER_UPDATE = "protocol.player_update"
        LEAVE_GAME = "protocol.leave_game"
