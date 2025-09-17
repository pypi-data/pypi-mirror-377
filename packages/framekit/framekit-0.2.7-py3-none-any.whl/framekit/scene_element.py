from typing import List, Union, TYPE_CHECKING, Literal
from .video_base import VideoBase

if TYPE_CHECKING:
    from typing import Self

class Scene(VideoBase):
    """Scene class for managing multiple video elements as a group.
    
    A Scene groups multiple VideoBase elements (text, images, videos, audio) and manages
    their collective timing. Scenes can be positioned at specific times in the timeline
    and automatically handle BGM duration adjustments.
    
    Attributes:
        elements: List of VideoBase elements in this scene
        start_time: Start time of the scene in seconds
        duration: Total duration of the scene in seconds
    """
    
    def __init__(self) -> None:
        """Initialize a new Scene with no elements."""
        super().__init__()  # Initialize VideoBase
        self.elements: List[Union[VideoBase, 'Scene']] = []
        # Note: start_time and duration are inherited from VideoBase
        # Override the inherited start_time to maintain Scene's None-based logic
        self.start_time: float = None  # None means not explicitly set
        self.duration: float = 0.0
        self._has_content_at_start: bool = False  # Track if scene has content at time 0
    
    def add(self, element: Union[VideoBase, 'Scene'], layer: Literal["top", "bottom"] = "top") -> 'Scene':
        """Add an element or scene to this scene.
        
        Args:
            element: VideoBase element (text, image, video, audio) or Scene to add
            layer: "top" to add on top (rendered last), "bottom" to add at bottom (rendered first)
            
        Returns:
            Self for method chaining
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement
        
        print(f"DEBUG: Adding element to scene, current scene duration: {self.duration}")
        print(f"DEBUG: Element type: {type(element).__name__}")
        if isinstance(element, Scene):
            print(f"DEBUG: Child scene duration: {element.duration}, start_time: {element.start_time}")
        else:
            print(f"DEBUG: Element duration: {element.duration}, start_time: {element.start_time}")
        
        # Add element based on layer parameter
        if layer == "bottom":
            self.elements.insert(0, element)
        else:  # layer == "top" (default)
            self.elements.append(element)
        
        # Handle duration calculation for different element types
        if isinstance(element, Scene):
            # シーンのstart_timeが明示的に設定されていない場合（Noneの場合）、
            # 前のシーンの終了時間を開始時間として設定（逐次再生）
            if element.start_time is None:
                # 子シーンが0秒時点でコンテンツを持っているかチェック
                child_has_content_at_start = self._scene_has_content_at_time(element, 0.0)
                
                if child_has_content_at_start and not self._has_content_at_start:
                    # 子シーンに0秒時点でコンテンツがあり、親シーンにまだ0秒コンテンツがない場合
                    # 子シーンを0秒から開始させる
                    element.start_time = 0.0
                    self._has_content_at_start = True
                    print(f"DEBUG: Setting child scene start_time to 0.0")
                else:
                    # 通常の逐次配置
                    last_scene_end_time = 0.0
                    print(f"DEBUG: Calculating sequential placement, existing elements: {len(self.elements)-1}")
                    for i, existing_element in enumerate(self.elements[:-1]):  # Exclude the just-added element
                        if isinstance(existing_element, Scene):
                            existing_start = existing_element.start_time if existing_element.start_time is not None else 0.0
                            existing_end = existing_start + existing_element.duration
                            print(f"DEBUG: Existing scene {i}: start={existing_start}, duration={existing_element.duration}, end={existing_end}")
                            last_scene_end_time = max(last_scene_end_time, existing_end)
                    element.start_time = last_scene_end_time
                    print(f"DEBUG: Setting child scene start_time to {element.start_time}")
            
            # For nested scenes, calculate end time based on scene's own timing
            element_start = element.start_time if element.start_time is not None else 0.0
            scene_end_time = element_start + element.duration
            print(f"DEBUG: Child scene end time: {element_start} + {element.duration} = {scene_end_time}")
            old_duration = self.duration
            self.duration = max(self.duration, scene_end_time)
            print(f"DEBUG: Parent scene duration updated: {old_duration} -> {self.duration}")
        else:
            # BGMモードでないオーディオ要素とループモードでないビデオ/画像要素と他の要素のみがシーン時間に影響
            is_bgm_audio = isinstance(element, AudioElement) and getattr(element, 'loop_until_scene_end', False)
            is_loop_video = isinstance(element, VideoElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
            is_loop_image = isinstance(element, ImageElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
            
            if not (is_bgm_audio or is_loop_video or is_loop_image):
                element_end_time = element.start_time + element.duration
                old_duration = self.duration
                self.duration = max(self.duration, element_end_time)
                print(f"DEBUG: Non-scene element, duration updated: {old_duration} -> {self.duration}")
        
        # BGMモードのオーディオ要素とループモードのビデオ/画像要素の持続時間を更新（シーン時間決定後）
        self._update_loop_element_durations()
        return self
    
    def _scene_has_content_at_time(self, scene: 'Scene', time: float) -> bool:
        """Check if a scene has any visible content at the specified time.
        
        Args:
            scene: Scene to check
            time: Time to check (relative to scene start)
            
        Returns:
            True if scene has visible content at the specified time
        """
        for element in scene.elements:
            if isinstance(element, Scene):
                # Recursively check nested scenes
                element_start = element.start_time if element.start_time is not None else 0.0
                if element_start <= time < element_start + element.duration:
                    if self._scene_has_content_at_time(element, time - element_start):
                        return True
            else:
                # Check if non-scene element is visible at this time
                if element.start_time <= time < element.start_time + element.duration:
                    return True
        return False
    
    def _update_loop_element_durations(self) -> None:
        """Update loop element durations to match scene length.
        
        This method finds all audio, video, and image elements with loop_until_scene_end=True
        and updates their duration to match the scene's total duration.
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement
        
        for element in self.elements:
            if isinstance(element, Scene):
                # For nested scenes, recursively update their loop elements
                element._update_loop_element_durations()
            elif isinstance(element, AudioElement) and element.loop_until_scene_end:
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, VideoElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, ImageElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
    
    def start_at(self, time: float) -> 'Scene':
        """Set the start time of this scene.
        
        Args:
            time: Start time in seconds
            
        Returns:
            Self for method chaining
        """
        self.start_time = time
        return self
    
    def is_visible_at(self, time: float) -> bool:
        """Check if scene is visible at the specified time.
        
        Overrides VideoBase method to handle Scene's None start_time.
        
        Args:
            time: Time in seconds to check
            
        Returns:
            True if scene is visible at the given time
        """
        start_time = self.start_time if self.start_time is not None else 0.0
        return start_time <= time < (start_time + self.duration)
    
    def calculate_size(self) -> None:
        """Calculate scene size based on contained elements.
        
        For Scene objects, size is determined by the bounding box of all contained elements.
        This is required by VideoBase interface.
        """
        # Scene size is conceptual - it contains other elements
        # For now, we'll set a default size, but this could be enhanced
        # to calculate actual bounding box of all elements
        self.width = 0
        self.height = 0
    
    def render(self, time: float) -> None:
        """Render all elements in this scene at the given time.
        
        This method now implements the VideoBase interface properly.
        
        Args:
            time: Current time in seconds (when called from VideoBase context,
                  this is scene-relative time; when called from MasterScene,
                  this needs time coordinate transformation)
        """
        # First, update animated properties as required by VideoBase
        self.update_animated_properties(time)
        
        # Check if the scene should be visible at this time
        if not self.is_visible_at(time):
            return
        
        # Calculate scene-relative time
        # For compatibility with existing behavior, we need to handle both:
        # 1. Direct calls from MasterScene (time is absolute)
        # 2. Calls from parent Scene (time is already relative)
        
        # If this is a top-level scene call (from MasterScene), 
        # time is absolute and we need to make it relative
        start_time = self.start_time if self.start_time is not None else 0.0
        
        # Check if we're being called as a nested scene (time < self.duration indicates relative time)
        # or as a top-level scene (time >= start_time indicates absolute time)
        if time >= start_time and self.start_time is not None:
            # This looks like absolute time from MasterScene
            scene_time = time - start_time
        else:
            # This looks like relative time from parent scene
            scene_time = time
        
        # Bound check for scene duration
        if scene_time < 0 or scene_time > self.duration:
            return
        
        # Render all elements with scene-relative time
        for element in self.elements:
            element.render(scene_time)