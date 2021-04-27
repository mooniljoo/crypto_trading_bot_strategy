from logic.strategy import Strategy
from api.bitmexAPI import BitmexAPI
from api.simulAPI import SimulAPI
from simulator import Simulator

from time import sleep


class Main:
    '''
    Main App
    '''

    def __init__(self) -> None:
        self.runningState = True
        self.bitmexapi = BitmexAPI()
        self.simulator = Simulator()

    def run(self) -> None:
        '''Run the Trader'''
        while self.runningState:
            print(self.simulator.run())

            strategy = Strategy(self.bitmexapi)
            # print(strategy.volatility_breakout())
            print(eval(f"strategy.{self.simulator.run()}()"))
            sleep(1)

    def stopRunning(self) -> None:
        '''Stop the Trader.'''
        self.runningState = False


if __name__ == "__main__":
    main = Main()
    main.run()
