from RealtimeSTT import AudioToTextRecorder
from typing import List
from modules.assistant_config import get_config
from modules.base_assistant import PlainAssistant
from modules.utils import create_session_logger_id, setup_logging
import typer
import logging

app = typer.Typer()


@app.command()
def ping():
    print("pong")


@app.command()
def chat():
    """Start a chat session with the plain assistant using speech input"""
    # Create session and logging
    session_id = create_session_logger_id()
    logger = setup_logging(session_id)
    logger.info(f"🚀 Starting chat session {session_id}")

    # Create assistant
    assistant = PlainAssistant(logger, session_id)

    # Configure STT recorder
    recorder = AudioToTextRecorder(
        spinner=True,
        model="tiny.en",
        language="en",
        print_transcription_time=True,
    )

    def process_text(text):
        """Process user speech input"""
        try:
            # Clean the text by removing symbols and whitespace from start/end
            text = text.strip().strip('.,!?;:"\'-')
            
            assistant_name = get_config("base_assistant.assistant_name")
            if assistant_name.lower() not in text.lower():
                logger.info(f"🤖 Not {assistant_name} - ignoring")
                return

            # Split text into words and find the word after assistant name
            words = text.lower().split()
            assistant_index = next(i for i, word in enumerate(words) if assistant_name.lower() in word)
            
            # Check if there's a next word and if it's an exit command
            if len(words) > assistant_index + 1 and words[assistant_index + 1] in ["exit", "quit"]:
                logger.info("👋 Exiting chat session")
                return False

            # Process input and get response
            recorder.stop()
            response = assistant.process_text(text)
            logger.info(f"🤖 Response: {response}")
            recorder.start()

            return True

        except Exception as e:
            logger.error(f"❌ Error occurred: {str(e)}")
            raise

    try:
        print("🎤 Speak now... (say 'exit' or 'quit' to end)")
        while True:
            recorder.text(process_text)

    except KeyboardInterrupt:
        logger.info("👋 Session ended by user")
        raise KeyboardInterrupt
    except Exception as e:
        logger.error(f"❌ Error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    app()
