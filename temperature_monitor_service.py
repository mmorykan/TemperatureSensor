import argparse
import time
from concurrent import futures
import grpc
import psutil
import temperature_monitor_pb2
import temperature_monitor_pb2_grpc
"""
This is a server to monitor the current temperature of the gunicorn raspberry pi using gRPC.
"""

class TemperatureMonitor(temperature_monitor_pb2_grpc.TemperatureMonitorServicer):
    def __init__(self):
        """
        Sets up the intial values for the maximum and minimum temperatures of the pi
        """
        self.max_temp = 40.0 if not self.psutil_exists() else psutil.sensors_temperatures()['bcm2835_thermal'][0].current
        self.min_temp = self.max_temp


    def psutil_exists(self):
        """
        Determines whether or not psutil.sensors_temperatures() exists on the host machine
        """
        return hasattr(psutil, 'sensors_temperatures')
        

    def get_current_temperature(self):
        """
        Returns the current temperature of the raspberry pi and updates its maximum and minimum temperatures
        """
        if self.psutil_exists():
            current_temperature = temperature_monitor_pb2.Temperature(celsius=
                psutil.sensors_temperatures()['bcm2835_thermal'][0].current)
            self.update_max_min(current_temperature)
            return current_temperature
        else:
            return temperature_monitor_pb2.Temperature(celsius=40.0)


    def CurrentTemperature(self, request, context):
        """
        Returns the current temperature
        """
        return self.get_current_temperature()


    def update_max_min(self, temperature):
        """
        Updates the maximum and minimum temperatures of the raspberry pi
        """
        if temperature.celsius > self.max_temp:
            self.max_temp = temperature.celsius
        elif temperature.celsius < self.min_temp:
            self.min_temp = temperature.celsius


    def Temperatures(self, request, context):
        """
        Returns multiple temperatures for the requested amount of time and updates the maximum and minimum 
        temperatures of the pi accordingly
        """
        while context.is_active():
            yield self.get_current_temperature()
            time.sleep(request.seconds)


    def MinMaxTemperature(self, request, context):
        """
        Returns the minimum and maximum temperatures from the pi
        """
        return temperature_monitor_pb2.MinMax(min=self.min_temp, max=self.max_temp)


    def StressTest(self, request, context):
        """
        Performs a stress test on the pi
        Basically just runs a loop for the requesed amount of time 
        """
        stress_number = 0
        start = time.monotonic()
        while (time.monotonic() - start) < request.seconds:
            stress_number += 1

        return temperature_monitor_pb2.Empty()


def main():
    """
    Parses argument for the port 
    Starts the server on the given port
    """
    parser = argparse.ArgumentParser(description='Obtain the current temperature on the raspberry pi')
    parser.add_argument('--port', type=int, help='The port number to connect to the raspberry pi', default=50051)
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))    
    temperature_monitor_pb2_grpc.add_TemperatureMonitorServicer_to_server(TemperatureMonitor(), server)    

    server.add_insecure_port(f'[::]:{args.port}')    
    server.start()    
    server.wait_for_termination()


if __name__ == '__main__':
    main()
