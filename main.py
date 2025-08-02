from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import urllib.parse
import logging

# Set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)

class GoogleMapsRoutesExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    
    def extract_params(self, input_str: str) -> tuple[str, str]:
        """Extract origin and destination from input string"""
        if " to " not in input_str:
            return "", ""
        
        parts = input_str.split(" to ", 1)  # Split only on first occurrence
        if len(parts) != 2:
            return "", ""
            
        origin = parts[0].strip()
        destination = parts[1].strip()
        return origin, destination
    
    def create_maps_url(self, origin: str, destination: str) -> str:
        """Create Google Maps URL with proper encoding"""
        origin_encoded = urllib.parse.quote(origin)
        destination_encoded = urllib.parse.quote(destination)
        return f"https://www.google.com/maps/dir/?api=1&origin={origin_encoded}&destination={destination_encoded}"
    
    def on_event(self, event, extension):
        try:
            logger.info(f"Event triggered with query: {event.get_argument()}")
            
            items = []
            query = event.get_argument() or ""
            
            # Always show something, even if empty
            if not query.strip():
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name='Google Maps Routes',
                    description='Type: <origin> to <destination> (e.g., "Vienna to Munich")',
                    on_enter=HideWindowAction()
                ))
                return RenderResultListAction(items)
            
            # Extract parameters from the query
            origin, destination = self.extract_params(query)
            
            if not origin or not destination:
                # Show help items when input is incomplete
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name='Search for a route',
                    description='Use format: <origin> to <destination>',
                    on_enter=HideWindowAction()
                ))
            else:
                # Create the maps URL
                maps_url = self.create_maps_url(origin, destination)
                logger.info(f"Generated URL: {maps_url}")
                
                # Add the main result item
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=f'Route from {origin} to {destination}',
                    description='Open Google Maps in the browser and search for a route',
                    on_enter=OpenUrlAction(maps_url)
                ))
                
                # Add reverse route option
                reverse_url = self.create_maps_url(destination, origin)
                items.append(ExtensionResultItem(
                    icon='images/icon.png',
                    name=f'Reverse: {destination} to {origin}',
                    description='Open reverse route in Google Maps',
                    on_enter=OpenUrlAction(reverse_url)
                ))
            
            logger.info(f"Returning {len(items)} items")
            return RenderResultListAction(items)
            
        except Exception as e:
            logger.error(f"Error in on_event: {e}")
            # Return a fallback item in case of errors
            items = [ExtensionResultItem(
                icon='images/icon.png',
                name='Error occurred',
                description=f'Error: {str(e)}',
                on_enter=HideWindowAction()
            )]
            return RenderResultListAction(items)

if __name__ == '__main__':
    GoogleMapsRoutesExtension().run()