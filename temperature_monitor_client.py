import grpc
import temperature_monitor_pb2
import temperature_monitor_pb2_grpc


def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = temperature_monitor_pb2_grpc.TemperatureMonitorStub(channel)
        # for response in stub.list_Products(ProductInfo_pb2.Filter(filter='w')):
        #     print(response)

        # response = stub.StressTest(temperature_monitor_pb2.Time(seconds=1000))
        # print(response)

        # response = stub.CurrentTemperature(temperature_monitor_pb2.Empty())
        # print(response)

        # for temp in stub.Temperatures(temperature_monitor_pb2.Time(seconds=1)):
        #     print(temp)


if __name__ == '__main__':
    main()