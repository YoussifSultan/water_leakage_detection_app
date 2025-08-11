from flask import Flask, request

def calibrate_moisturevalue(val):
    moisturePercent = round(100.0 - (val / 4095.0) * 100.0)
    return moisturePercent

def create_server(update_queue):
    app = Flask(__name__)

    @app.route('/update', methods=['POST'])
    def receive_data():
        data = request.get_json()
        pipes =data.get('pipes')
        for pipe in pipes:    
            pipe_id = pipe.get('pipe_id')
            moisture = pipe.get('moisture')
            # Push to the queue
            print(f"{pipe_id} : {moisture}")
            update_queue.put((pipe_id, calibrate_moisturevalue( moisture)))
        
        return 'OK', 200

    return app

