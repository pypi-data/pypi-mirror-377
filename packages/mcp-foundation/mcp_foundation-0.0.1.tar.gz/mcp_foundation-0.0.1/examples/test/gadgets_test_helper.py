"""Gadgets testing helper for all transport types."""

import asyncio
from typing import Dict, Any, List, Optional


class GadgetsTestHelper:
    """Helper class for testing gadgets tools across all transports."""
    
    EXPECTED_GADGETS = [
        "calculate_fibonacci",
        "reverse_text", 
        "roll_dice",
        "generate_password",
        "system_info"
    ]
    
    GADGET_TEST_CASES = {
        "calculate_fibonacci": {
            "args": {"n": 8},
            "expected_in_result": ["0", "1", "1", "2", "3", "5", "8", "13"],
            "description": "Calculate Fibonacci sequence"
        },
        "reverse_text": {
            "args": {"text": "Hello MCP!"},
            "expected_in_result": ["!PCM olleH"],
            "description": "Reverse text string"
        },
        "roll_dice": {
            "args": {"sides": 6, "count": 2},
            "expected_contains": ["rolled", "dice", "total"],
            "description": "Roll dice simulation"
        },
        "generate_password": {
            "args": {"length": 12},
            "expected_length_check": 12,
            "description": "Generate secure password"
        },
        "system_info": {
            "args": {},
            "expected_contains": ["system", "platform"],
            "description": "Get system information"
        }
    }
    
    @staticmethod
    def find_gadgets_tools(tools_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find gadgets tools in a tools list."""
        gadgets_tools = []
        for tool in tools_list:
            tool_name = tool.get('name', '')
            if any(gadget in tool_name for gadget in GadgetsTestHelper.EXPECTED_GADGETS):
                gadgets_tools.append(tool)
        return gadgets_tools
    
    @staticmethod
    def validate_tool_result(tool_name: str, result: Dict[str, Any]) -> bool:
        """Validate a gadgets tool result."""
        if "error" in result:
            print(f"   ❌ {tool_name} returned error: {result['error']}")
            return False
        
        tool_result = result.get('result', {})
        content = tool_result.get('content', [])
        
        if not content:
            print(f"   ❌ {tool_name} returned no content")
            return False
        
        # Get the first content item's text
        result_text = str(content[0].get('text', '')) if content else ""
        
        if not result_text:
            print(f"   ❌ {tool_name} returned empty text")
            return False
        
        # Check test case expectations
        test_case = GadgetsTestHelper.GADGET_TEST_CASES.get(tool_name, {})
        
        if "expected_in_result" in test_case:
            for expected in test_case["expected_in_result"]:
                if expected not in result_text:
                    print(f"   ⚠️  {tool_name} result missing expected content: {expected}")
                    return False
        
        if "expected_contains" in test_case:
            for expected in test_case["expected_contains"]:
                if expected.lower() not in result_text.lower():
                    print(f"   ⚠️  {tool_name} result missing expected pattern: {expected}")
        
        if "expected_length_check" in test_case and tool_name == "generate_password":
            lines = result_text.split('\n')
            for line in lines:
                if 'Password:' in line or 'password:' in line:
                    password = line.split(':')[-1].strip()
                    if len(password) != test_case["expected_length_check"]:
                        print(f"   ⚠️  {tool_name} password length incorrect: expected {test_case['expected_length_check']}, got {len(password)}")
        
        print(f"   ✅ {tool_name} result validated")
        return True
    
    @staticmethod
    async def test_gadgets_tools_comprehensive(client, transport_name: str) -> Dict[str, bool]:
        """Test all available gadgets tools comprehensively."""
        print(f"🎮 Testing Gadgets Tools via {transport_name.upper()}")
        
        results = {}
        
        try:
            tools_response = await client.list_tools()
            if "error" in tools_response:
                print(f"   ❌ Failed to list tools: {tools_response['error']}")
                return {"tools_listing": False}
            
            tools_list = tools_response.get('result', {}).get('tools', [])
            total_tools = len(tools_list)
            print(f"   📊 Total tools available: {total_tools}")
            
            gadgets_tools = GadgetsTestHelper.find_gadgets_tools(tools_list)
            gadgets_count = len(gadgets_tools)
            print(f"   🎮 Gadgets tools found: {gadgets_count}")
            
            for tool in gadgets_tools:
                print(f"      - {tool['name']}: {tool.get('description', 'No description')}")
            
            results["tools_listing"] = True
            results["gadgets_found"] = gadgets_count > 0
            
            if gadgets_count == 0:
                print("   ⚠️  No gadgets tools found - cannot test tool execution")
                return results
            
            successful_calls = 0
            for tool in gadgets_tools:
                tool_name = tool['name']
                
                test_case = None
                for expected_tool, case in GadgetsTestHelper.GADGET_TEST_CASES.items():
                    if expected_tool in tool_name:
                        test_case = case
                        break
                
                if not test_case:
                    print(f"   ⚠️  No test case defined for {tool_name}")
                    continue
                
                print(f"   🧪 Testing {tool_name}: {test_case['description']}")
                
                try:
                    result = await client.call_tool(tool_name, test_case["args"])
                    
                    if GadgetsTestHelper.validate_tool_result(tool_name, result):
                        result_text = result.get("result", {}).get("content", [{}])[0].get("text", "")
                        if result_text:
                            display_text = result_text[:150] + "..." if len(result_text) > 150 else result_text
                            print(f"      ✅ Result: {display_text}")
                        
                        results[f"tool_{tool_name}"] = True
                        successful_calls += 1
                    else:
                        results[f"tool_{tool_name}"] = False
                        
                except Exception as e:
                    print(f"   ❌ {tool_name} call failed: {e}")
                    results[f"tool_{tool_name}"] = False
            
            results["tool_execution_summary"] = {
                "total_gadgets": gadgets_count,
                "successful_calls": successful_calls,
                "success_rate": successful_calls / gadgets_count if gadgets_count > 0 else 0
            }
            
            print(f"   📊 Gadgets test summary: {successful_calls}/{gadgets_count} tools working")
            
            results["gadgets_overall_success"] = (successful_calls / gadgets_count) >= 0.8 if gadgets_count > 0 else False
            
            return results
            
        except Exception as e:
            print(f"   ❌ Gadgets testing failed: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def test_quick_gadgets_validation(client, transport_name: str) -> bool:
        """Quick validation using just one or two gadgets tools."""
        print(f"🎮 Quick Gadgets Validation via {transport_name.upper()}")
        
        try:
            # Test Fibonacci (most reliable)
            print("   🧪 Testing calculate_fibonacci...")
            result = await client.call_tool("calculate_fibonacci", {"n": 5})
            
            if "error" in result:
                print(f"   ❌ Fibonacci test failed: {result['error']}")
                return False
            
            if GadgetsTestHelper.validate_tool_result("calculate_fibonacci", result):
                # Show actual result
                fib_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
                print(f"   ✅ Fibonacci test passed! Result: {fib_result[:100]}...")
                
                # Quick test of text reversal if available
                try:
                    print("   🧪 Testing reverse_text...")
                    result2 = await client.call_tool("reverse_text", {"text": "Test"})
                    if not ("error" in result2):
                        if GadgetsTestHelper.validate_tool_result("reverse_text", result2):
                            text_result = result2.get("result", {}).get("content", [{}])[0].get("text", "")
                            print(f"   ✅ Text reversal passed! Result: {text_result}")
                except:
                    pass  # Optional test
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"   ❌ Quick gadgets validation failed: {e}")
            return False
    
    @staticmethod
    def print_gadgets_summary(results: Dict[str, Any], transport_name: str):
        """Print a summary of gadgets test results."""
        print(f"\n🎮 Gadgets Test Summary for {transport_name.upper()}")
        print("-" * 50)
        
        if "error" in results:
            print(f"❌ Testing failed: {results['error']}")
            return
        
        # Basic checks
        if results.get("tools_listing", False):
            print("✅ Tools listing successful")
        else:
            print("❌ Tools listing failed")
            
        if results.get("gadgets_found", False):
            print("✅ Gadgets tools found")
        else:
            print("❌ No gadgets tools found")
            return
        
        # Individual tool results
        tool_results = {k: v for k, v in results.items() if k.startswith("tool_")}
        if tool_results:
            print(f"📊 Individual Tool Results:")
            for tool_key, success in tool_results.items():
                tool_name = tool_key.replace("tool_", "")
                status = "✅" if success else "❌"
                print(f"   {status} {tool_name}")
        
        # Summary
        if "tool_execution_summary" in results:
            summary = results["tool_execution_summary"]
            success_rate = summary["success_rate"] * 100
            print(f"\n📈 Success Rate: {success_rate:.1f}% ({summary['successful_calls']}/{summary['total_gadgets']})")
        
        # Overall assessment
        overall_success = results.get("gadgets_overall_success", False)
        if overall_success:
            print("🎉 Gadgets testing PASSED - E2E functionality confirmed!")
        else:
            print("⚠️  Gadgets testing shows issues - E2E may have problems")


# Quick validation function for use in other test files
async def quick_gadgets_test(client, transport_name: str) -> bool:
    """Quick gadgets test function for easy import."""
    return await GadgetsTestHelper.test_quick_gadgets_validation(client, transport_name)


# Comprehensive testing function for use in other test files  
async def comprehensive_gadgets_test(client, transport_name: str) -> Dict[str, Any]:
    """Comprehensive gadgets test function for easy import."""
    return await GadgetsTestHelper.test_gadgets_tools_comprehensive(client, transport_name)
