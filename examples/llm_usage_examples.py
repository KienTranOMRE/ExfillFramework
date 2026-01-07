"""
Examples of using the LLM service with Gemini and Qwen.

Run this file to see examples:
    python examples/llm_usage_examples.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_service import generate, chat, list_available_services, LLMClient


def example_1_simple_generation():
    """Example 1: Simple text generation"""
    print("\n" + "=" * 60)
    print("Example 1: Simple Text Generation with Gemini")
    print("=" * 60)

    prompt = "Explain what a neural network is in 2 sentences."

    try:
        response = generate(
            prompt=prompt,
            service="gemini",
            temperature=0.0
        )
        print(f"\nPrompt: {prompt}")
        print(f"\nResponse:\n{response}")
    except Exception as e:
        print(f"Error: {e}")


def example_2_generation_with_system_prompt():
    """Example 2: Generation with system prompt"""
    print("\n" + "=" * 60)
    print("Example 2: Generation with System Prompt")
    print("=" * 60)

    system_prompt = "You are a Python programming expert. Always provide concise, practical code examples."
    user_prompt = "How do I read a JSON file in Python?"

    try:
        response = generate(
            prompt=user_prompt,
            service="gemini",
            system_prompt=system_prompt,
            temperature=0.0
        )
        print(f"\nSystem: {system_prompt}")
        print(f"\nUser: {user_prompt}")
        print(f"\nAssistant:\n{response}")
    except Exception as e:
        print(f"Error: {e}")


def example_3_chat_conversation():
    """Example 3: Multi-turn chat conversation"""
    print("\n" + "=" * 60)
    print("Example 3: Multi-turn Chat Conversation")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What's its population?"}
    ]

    try:
        response = chat(
            messages=messages,
            service="gemini",
            temperature=0.0
        )
        print("\nConversation:")
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            print(f"{role}: {content}")

        print(f"\nAssistant: {response}")
    except Exception as e:
        print(f"Error: {e}")


def example_4_qwen_service():
    """Example 4: Using Qwen service"""
    print("\n" + "=" * 60)
    print("Example 4: Using Qwen (OpenAI-compatible API)")
    print("=" * 60)

    prompt = "What are the benefits of using vector databases?"

    try:
        response = generate(
            prompt=prompt,
            service="qwen",
            model="qwen-turbo",
            temperature=0.7,
            max_tokens=200
        )
        print(f"\nPrompt: {prompt}")
        print(f"\nResponse:\n{response}")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure QWEN_API_KEY and QWEN_BASE_URL are set in .env")


def example_5_llm_client_conversation():
    """Example 5: Using LLMClient for stateful conversation"""
    print("\n" + "=" * 60)
    print("Example 5: Stateful Conversation with LLMClient")
    print("=" * 60)

    try:
        # Create a client with system prompt
        client = LLMClient(
            service="gemini",
            system_prompt="You are a knowledgeable AI assistant specializing in technology.",
            temperature=0.5
        )

        # Have a conversation
        print("\nUser: What is machine learning?")
        response1 = client.send("What is machine learning?")
        print(f"Assistant: {response1}\n")

        print("User: Can you give me a simple example?")
        response2 = client.send("Can you give me a simple example?")
        print(f"Assistant: {response2}\n")

        # Show conversation history
        print("\n--- Conversation History ---")
        history = client.get_history()
        print(f"Total messages: {len(history)}")

    except Exception as e:
        print(f"Error: {e}")


def example_6_comparison():
    """Example 6: Compare Gemini and Qwen responses"""
    print("\n" + "=" * 60)
    print("Example 6: Compare Gemini vs Qwen")
    print("=" * 60)

    prompt = "What is the difference between AI and ML?"

    print(f"\nPrompt: {prompt}\n")

    # Try Gemini
    try:
        print("--- Gemini Response ---")
        gemini_response = generate(
            prompt=prompt,
            service="gemini",
            temperature=0.0
        )
        print(gemini_response)
    except Exception as e:
        print(f"Gemini Error: {e}")

    print()

    # Try Qwen
    try:
        print("--- Qwen Response ---")
        qwen_response = generate(
            prompt=prompt,
            service="qwen",
            temperature=0.0
        )
        print(qwen_response)
    except Exception as e:
        print(f"Qwen Error: {e}")
        print("Note: Make sure QWEN_API_KEY and QWEN_BASE_URL are set in .env")


def example_7_json_extraction():
    """Example 7: Extract structured JSON data"""
    print("\n" + "=" * 60)
    print("Example 7: Structured JSON Extraction")
    print("=" * 60)

    system_prompt = """You are a data extraction assistant.
Extract information and return it in valid JSON format only.
Do not include any explanation, just the JSON."""

    user_prompt = """Extract the following information from this text and return as JSON:

Text: "John Smith is a 35-year-old software engineer living in San Francisco.
He works at TechCorp and specializes in machine learning."

Required fields:
- name
- age
- occupation
- city
- company
- specialization
"""

    try:
        response = generate(
            prompt=user_prompt,
            service="gemini",
            system_prompt=system_prompt,
            temperature=0.0
        )
        print(f"\nExtracted JSON:\n{response}")

        # Try to parse the JSON
        import json
        try:
            data = json.loads(response)
            print("\n✓ Valid JSON!")
            print(f"Parsed data: {data}")
        except json.JSONDecodeError:
            print("\n✗ Invalid JSON returned")

    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("LLM Service Usage Examples")
    print("=" * 60)

    # Show available services first
    list_available_services()

    # Run examples
    examples = [
        example_1_simple_generation,
        example_2_generation_with_system_prompt,
        example_3_chat_conversation,
        example_4_qwen_service,
        example_5_llm_client_conversation,
        example_6_comparison,
        example_7_json_extraction,
    ]

    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nExample failed: {e}")

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
