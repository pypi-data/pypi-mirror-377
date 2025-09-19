from lolgram_inapp_bot import LolgramInAppBot, Update

def test_bot():
    bot = LolgramInAppBot("test_api_key", base_url="http://localhost:3000")
    def handle_message(update: Update):
        print(f"Test message: {update.data['text']}")
        bot.send_action("send_message", {"text": "Test response"})
    
    bot.add_handler("message", handle_message)
    # Simulate an update (requires server running locally)
    # bot.start_polling()  # Uncomment to test with real server
    print("Test setup complete")

if __name__ == "__main__":
    test_bot()