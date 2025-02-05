import pygame
import pygame.camera
import time
import schedule
import asyncio
from telegram.ext import ApplicationBuilder
from datetime import datetime
from pathlib import Path

class PrinterMonitor:
    def __init__(self, token, chat_id, camera_id=0):
        """
        Initialize the printer monitor
        token: Your Telegram bot token
        chat_id: Your Telegram chat ID
        camera_id: Webcam device number (usually 0)
        """
        # Initialize pygame camera
        pygame.camera.init()
        cameras = pygame.camera.list_cameras()
        if not cameras:
            raise Exception("No cameras found")
            
        self.camera = pygame.camera.Camera(cameras[camera_id], (640, 480))
        self.app = ApplicationBuilder().token(token).build()
        self.chat_id = chat_id
        self.image_dir = Path('printer_shots')
        self.image_dir.mkdir(exist_ok=True)

    async def capture_and_send(self):
        """Capture image and send to Telegram"""
        try:
            # Start the camera
            self.camera.start()
            
            # Get image
            image = self.camera.get_image()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = self.image_dir / f"print_{timestamp}.jpg"
            
            # Save image
            pygame.image.save(image, str(image_path))
            
            # Stop the camera
            self.camera.stop()
            
            # Send to Telegram
            async with self.app:
                await self.app.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=open(image_path, 'rb'),
                    caption=f"Print Status - {timestamp}"
                )
            
            # Cleanup old images
            self.cleanup_old_images()
            
        except Exception as e:
            error_msg = f"Error capturing/sending image: {str(e)}"
            print(error_msg)
            try:
                async with self.app:
                    await self.app.bot.send_message(chat_id=self.chat_id, text=error_msg)
            except:
                print("Could not send error message to Telegram")

    def cleanup_old_images(self, hours=24):
        """Delete images older than specified hours"""
        current_time = time.time()
        for image_path in self.image_dir.glob("*.jpg"):
            if (current_time - image_path.stat().st_mtime) > (hours * 3600):
                image_path.unlink()

    def scheduled_capture(self):
        """Helper to run async capture in the scheduler"""
        asyncio.run(self.capture_and_send())

    def start_monitoring(self, interval_minutes=30):
        """Start the monitoring schedule"""
        schedule.every(interval_minutes).minutes.do(self.scheduled_capture)
        
        print(f"Monitoring started. Capturing every {interval_minutes} minutes...")
        
        # Initial capture
        self.scheduled_capture()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    # Replace these with your actual values
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    CAMERA_ID = 0  # Usually 0 for first camera
    INTERVAL_MINUTES = 15 

    monitor = PrinterMonitor(
        token=TELEGRAM_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        camera_id=CAMERA_ID
    )
    
    monitor.start_monitoring(INTERVAL_MINUTES)
