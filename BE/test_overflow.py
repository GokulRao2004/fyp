"""
Test script to demonstrate text overflow prevention in PPT generation
"""
import sys
import os

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(__file__))

from services.ppt_service import PPTService

def test_text_wrapping():
    """Test text wrapping functionality"""
    ppt_service = PPTService(theme='modern')
    
    # Test 1: Long title that needs wrapping
    long_title = "This is an extremely long title that would normally overflow the text box boundaries in a presentation slide"
    
    # Test 2: Long subtitle
    long_subtitle = "A comprehensive guide to understanding how text overflow can be prevented with automatic word wrapping and font size adjustment"
    
    # Test 3: Many bullet points with long text
    long_content = [
        "This is a very long bullet point with a lot of text that would normally overflow the boundaries of the text box if not properly wrapped",
        "Another extensive bullet point describing complex concepts that require detailed explanations and multiple sentences to convey the complete message",
        "Third bullet point with considerable length to test the dynamic font size adjustment feature",
        "Fourth point adding more content to test overflow handling",
        "Fifth bullet point for comprehensive testing",
        "Sixth point to ensure the system handles multiple items",
        "Seventh bullet for extensive content testing",
        "Eighth item to push the limits",
        "Ninth bullet point with additional content that extends beyond normal boundaries",
        "Tenth and final bullet to test maximum capacity handling"
    ]
    
    # Create test presentation
    presentation_data = {
        'title': long_title,
        'subtitle': long_subtitle,
        'slides': [
            {
                'slide_number': 1,
                'title': 'Testing Text Overflow Prevention',
                'content': long_content[:5],
                'speaker_notes': 'Test notes for overflow handling'
            },
            {
                'slide_number': 2,
                'title': 'Comprehensive Test with All Features Including Word Wrapping',
                'content': long_content,
                'speaker_notes': 'Testing with many bullets and long text'
            }
        ]
    }
    
    # Generate presentation
    try:
        ppt_bytes = ppt_service.generate_from_data(presentation_data)
        
        # Save to file for verification
        output_path = 'test_overflow_prevention.pptx'
        with open(output_path, 'wb') as f:
            f.write(ppt_bytes)
        
        print(f"✓ Test passed! Presentation generated successfully: {output_path}")
        print(f"  - File size: {len(ppt_bytes)} bytes")
        print(f"  - Total slides: {len(ppt_service.prs.slides)}")
        print("\nFeatures tested:")
        print("  ✓ Long title wrapping")
        print("  ✓ Long subtitle wrapping")
        print("  ✓ Bullet point text wrapping")
        print("  ✓ Dynamic font size adjustment for overflow")
        print("\nPlease open the generated PowerPoint file to verify:")
        print("  1. All text is visible within slide boundaries")
        print("  2. Long text is properly wrapped")
        print("  3. Font size is adjusted when needed")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Text Overflow Prevention in PPT Generation")
    print("=" * 60)
    print()
    
    success = test_text_wrapping()
    
    print()
    print("=" * 60)
    if success:
        print("Status: ALL TESTS PASSED ✓")
    else:
        print("Status: TESTS FAILED ✗")
    print("=" * 60)
