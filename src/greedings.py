from datetime import datetime

class Greedings:
    def __init__(self):
        current_time = datetime.now().time()
        hour = current_time.hour
        
        if 5 <= hour < 12:
            self.greeting = "Good Morning"
        elif 12 <= hour < 19:
            self.greeting = "Good Afternoon"
        else:
            self.greeting = "Good Night"
    
    def __str__(self) -> str:
        return f"{self.greeting}"