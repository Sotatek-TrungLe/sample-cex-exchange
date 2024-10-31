import asyncio
import json
from utils import consume_orders, publish_trade
from order_book import OrderBook
from logger import logger  # Import logger

async def run_matching_engine(order_book):
    while True:
        # Attempt to match orders based on the selected algorithm
        trades = order_book.match_orders()
        logger.debug(f"Matching engine found trades: {trades}")

        # Publish each trade event immediately and log it
        for trade in trades:
            publish_trade(trade)
            logger.info(f"Trade executed: {trade}")

        # Yield control for high-throughput processing
        await asyncio.sleep(0)

async def main():
    # Initialize the OrderBook 
    order_book = OrderBook()

    # Run the consumer and matching engine concurrently
    logger.info("Starting consumer_task ....")
    consumer_task = asyncio.create_task(asyncio.to_thread(consume_orders, order_book))

    logger.info("Starting matching_task ....")
    matching_task = asyncio.create_task(run_matching_engine(order_book))
    
    await asyncio.gather(consumer_task, matching_task)

if __name__ == "__main__":
    logger.info("Matching engine running ....")
    asyncio.run(main())