
import time, json, matplotlib.pyplot as plt, pandas as pd, numpy as np
from datetime import datetime
from agentsiq.agent import Agent
from agentsiq.collab import Collab
from agentsiq.router import ModelRouter
from agentsiq.decision_store import latest_decisions

def run_comprehensive_benchmark():
    """Run a comprehensive benchmark comparing all available models"""
    print("🚀 Starting AgentsIQ Comprehensive Benchmark")
    print("=" * 50)
    
    # Initialize router and get all available models
    router = ModelRouter()
    available_models = list(router.profiles.keys())
    print(f"📊 Testing {len(available_models)} models: {', '.join(available_models)}")
    
    # Define comprehensive test tasks
    test_tasks = [
        {
            "name": "Code Generation",
            "prompt": "Write a Python function to find the longest common subsequence between two strings. Include time complexity analysis.",
            "category": "coding"
        },
        {
            "name": "Summarization",
            "prompt": "Summarize the key concepts of machine learning in exactly 5 bullet points, focusing on practical applications.",
            "category": "summarization"
        },
        {
            "name": "Creative Writing",
            "prompt": "Write a short story (100 words) about an AI that discovers emotions. Make it engaging and thought-provoking.",
            "category": "creative"
        },
        {
            "name": "Technical Analysis",
            "prompt": "Explain the differences between REST and GraphQL APIs, including pros/cons and use cases for each.",
            "category": "technical"
        },
        {
            "name": "Problem Solving",
            "prompt": "Design a simple algorithm to detect if a linked list has a cycle. Provide step-by-step explanation.",
            "category": "problem_solving"
        }
    ]
    
    # Results storage
    results = []
    model_performance = {model: {"responses": [], "times": [], "costs": []} for model in available_models}
    
    print(f"\n🧪 Running {len(test_tasks)} test scenarios...")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n📝 Task {i}/{len(test_tasks)}: {task['name']}")
        print(f"Category: {task['category']}")
        
        # Test each model with this task
        for model in available_models:
            start_time = time.time()
            
            try:
                # Get model selection and response
                selected_model = router.select_model(task['prompt'], preferred=model)
                response, quality_score = router.call_model(selected_model, task['prompt'])
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Calculate cost (simplified)
                profile = router.profiles.get(selected_model, {"cost": 1.0})
                estimated_cost = profile["cost"] * (len(task['prompt']) + len(response)) / 1000.0
                
                # Store results
                result = {
                    "task_name": task['name'],
                    "task_category": task['category'],
                    "model": selected_model,
                    "response": response[:200] + "..." if len(response) > 200 else response,
                    "response_time": response_time,
                    "quality_score": quality_score,
                    "estimated_cost": estimated_cost,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
                
                model_performance[selected_model]["responses"].append(response)
                model_performance[selected_model]["times"].append(response_time)
                model_performance[selected_model]["costs"].append(estimated_cost)
                
                print(f"  ✅ {selected_model}: {response_time:.2f}s, ${estimated_cost:.4f}, quality: {quality_score:.2f}")
                
            except Exception as e:
                print(f"  ❌ {model}: Error - {str(e)}")
                continue
            
            time.sleep(0.1)  # Rate limiting
    
    # Generate comprehensive analysis
    print("\n📊 GENERATING ANALYSIS AND VISUALIZATIONS")
    print("=" * 50)
    
    # Create DataFrame for analysis
    df = pd.DataFrame(results)
    
    # 1. Model Performance Summary
    print("\n🏆 MODEL PERFORMANCE SUMMARY")
    print("-" * 30)
    
    summary_stats = []
    for model in available_models:
        if model_performance[model]["times"]:
            stats = {
                "Model": model,
                "Avg Response Time (s)": np.mean(model_performance[model]["times"]),
                "Avg Cost ($)": np.mean(model_performance[model]["costs"]),
                "Avg Quality Score": np.mean([r["quality_score"] for r in results if r["model"] == model]),
                "Tasks Completed": len(model_performance[model]["times"])
            }
            summary_stats.append(stats)
    
    summary_df = pd.DataFrame(summary_stats)
    print(summary_df.to_string(index=False, float_format='%.4f'))
    
    # 2. Create comprehensive model summary
    create_model_summary_table(available_models, df)
    
    # 3. Create visualizations
    create_performance_visualizations(df, model_performance, available_models)
    
    # 3. Cost Analysis
    print("\n💰 COST ANALYSIS")
    print("-" * 20)
    total_costs = df.groupby('model')['estimated_cost'].sum().sort_values(ascending=False)
    print("Total costs by model:")
    for model, cost in total_costs.items():
        print(f"  {model}: ${cost:.4f}")
    
    # 4. Speed Analysis
    print("\n⚡ SPEED ANALYSIS")
    print("-" * 20)
    avg_times = df.groupby('model')['response_time'].mean().sort_values()
    print("Average response times:")
    for model, time_val in avg_times.items():
        print(f"  {model}: {time_val:.2f}s")
    
    # 5. Quality Analysis
    print("\n🎯 QUALITY ANALYSIS")
    print("-" * 20)
    avg_quality = df.groupby('model')['quality_score'].mean().sort_values(ascending=False)
    print("Average quality scores:")
    for model, quality in avg_quality.items():
        print(f"  {model}: {quality:.3f}")
    
    # 6. Task-specific analysis
    print("\n📋 TASK-SPECIFIC ANALYSIS")
    print("-" * 30)
    for category in df['task_category'].unique():
        category_df = df[df['task_category'] == category]
        best_model = category_df.loc[category_df['quality_score'].idxmax()]
        fastest_model = category_df.loc[category_df['response_time'].idxmin()]
        cheapest_model = category_df.loc[category_df['estimated_cost'].idxmin()]
        
        print(f"\n{category.upper()}:")
        print(f"  Best Quality: {best_model['model']} (score: {best_model['quality_score']:.3f})")
        print(f"  Fastest: {fastest_model['model']} ({fastest_model['response_time']:.2f}s)")
        print(f"  Cheapest: {cheapest_model['model']} (${cheapest_model['estimated_cost']:.4f})")
    
    # Save detailed results
    results_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    print("\n🎉 Benchmark completed! Check the generated charts for visual analysis.")
    return results, summary_df

def create_model_summary_table(available_models, df):
    """Create a comprehensive model summary table"""
    print("\n📊 COMPREHENSIVE MODEL SUMMARY")
    print("=" * 80)
    
    router = ModelRouter()
    usage_counts = df['model'].value_counts() if not df.empty else pd.Series()
    
    # Create summary data
    summary_data = []
    for model in available_models:
        profile = router.profiles[model]
        usage_count = usage_counts.get(model, 0)
        
        # Calculate actual performance if model was used
        if usage_count > 0 and not df.empty:
            model_data = df[df['model'] == model]
            avg_time = model_data['response_time'].mean()
            avg_cost = model_data['estimated_cost'].mean()
            avg_quality = model_data['quality_score'].mean()
        else:
            avg_time = profile['latency']
            avg_cost = profile['cost'] * 0.1  # Scaled for display
            avg_quality = profile['quality']
        
        summary_data.append({
            'Model': model.split(':')[-1],
            'Provider': model.split(':')[0],
            'Config Cost': f"${profile['cost']:.3f}",
            'Config Latency': f"{profile['latency']:.2f}s",
            'Config Quality': f"{profile['quality']:.2f}",
            'Used': usage_count,
            'Avg Time': f"{avg_time:.2f}s",
            'Avg Cost': f"${avg_cost:.4f}",
            'Avg Quality': f"{avg_quality:.3f}"
        })
    
    # Create and display DataFrame
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # Add insights
    print("\n🔍 KEY INSIGHTS:")
    print("-" * 40)
    
    if not df.empty:
        most_used = usage_counts.idxmax() if len(usage_counts) > 0 else "None"
        cheapest_used = df.loc[df['estimated_cost'].idxmin(), 'model'] if len(df) > 0 else "None"
        fastest_used = df.loc[df['response_time'].idxmin(), 'model'] if len(df) > 0 else "None"
        highest_quality = df.loc[df['quality_score'].idxmax(), 'model'] if len(df) > 0 else "None"
        
        print(f"• Most Used Model: {most_used.split(':')[-1] if most_used != 'None' else 'None'}")
        print(f"• Cheapest Used: {cheapest_used.split(':')[-1] if cheapest_used != 'None' else 'None'}")
        print(f"• Fastest Used: {fastest_used.split(':')[-1] if fastest_used != 'None' else 'None'}")
        print(f"• Highest Quality: {highest_quality.split(':')[-1] if highest_quality != 'None' else 'None'}")
        
        # Cost savings analysis
        total_cost = df['estimated_cost'].sum()
        gpt4o_cost = router.profiles.get('openai:gpt-4o', {}).get('cost', 5.0)
        potential_gpt4o_cost = gpt4o_cost * len(df) * 0.1  # Scaled
        savings = potential_gpt4o_cost - total_cost
        
        print(f"• Total Cost: ${total_cost:.4f}")
        print(f"• Potential GPT-4o Cost: ${potential_gpt4o_cost:.4f}")
        print(f"• Total Savings: ${savings:.4f} ({savings/potential_gpt4o_cost*100:.1f}%)")
    
    print(f"• Available Models: {len(available_models)}")
    print(f"• Models Used: {len(usage_counts)}")
    print(f"• Unused Models: {len(available_models) - len(usage_counts)}")

def create_performance_visualizations(df, model_performance, available_models):
    """Create comprehensive performance visualizations"""
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig = plt.figure(figsize=(24, 18))
    
    # Get all models from config (including those not used in benchmark)
    router = ModelRouter()
    all_models = list(router.profiles.keys())
    
    # 1. Response Time Comparison - All Models
    plt.subplot(3, 3, 1)
    avg_times = df.groupby('model')['response_time'].mean().sort_values()
    
    # Create data for all models (use config defaults for unused models)
    all_times = []
    all_labels = []
    for model in all_models:
        if model in avg_times.index:
            all_times.append(avg_times[model])
        else:
            # Use config latency as default
            all_times.append(router.profiles[model]['latency'])
        all_labels.append(model.split(':')[-1])
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(all_times)))
    bars = plt.bar(range(len(all_times)), all_times, color=colors)
    plt.title('Response Time Comparison (All Models)', fontsize=14, fontweight='bold')
    plt.xlabel('Models')
    plt.ylabel('Response Time (seconds)')
    plt.xticks(range(len(all_times)), all_labels, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.2f}s', ha='center', va='bottom', fontsize=8)
    
    # 2. Cost Comparison - All Models
    plt.subplot(3, 3, 2)
    avg_costs = df.groupby('model')['estimated_cost'].mean().sort_values(ascending=False)
    
    # Create data for all models
    all_costs = []
    all_cost_labels = []
    for model in all_models:
        if model in avg_costs.index:
            all_costs.append(avg_costs[model])
        else:
            # Use config cost as default (scaled for visualization)
            config_cost = router.profiles[model]['cost']
            all_costs.append(config_cost * 0.1)  # Scale for better visualization
        all_cost_labels.append(model.split(':')[-1])
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(all_costs)))
    bars = plt.bar(range(len(all_costs)), all_costs, color=colors)
    plt.title('Cost Comparison (All Models)', fontsize=14, fontweight='bold')
    plt.xlabel('Models')
    plt.ylabel('Cost ($)')
    plt.xticks(range(len(all_costs)), all_cost_labels, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'${height:.4f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Quality Score Comparison - All Models
    plt.subplot(3, 3, 3)
    avg_quality = df.groupby('model')['quality_score'].mean().sort_values(ascending=False)
    
    # Create data for all models
    all_qualities = []
    all_quality_labels = []
    for model in all_models:
        if model in avg_quality.index:
            all_qualities.append(avg_quality[model])
        else:
            # Use config quality as default
            all_qualities.append(router.profiles[model]['quality'])
        all_quality_labels.append(model.split(':')[-1])
    
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(all_qualities)))
    bars = plt.bar(range(len(all_qualities)), all_qualities, color=colors)
    plt.title('Quality Score Comparison (All Models)', fontsize=14, fontweight='bold')
    plt.xlabel('Models')
    plt.ylabel('Quality Score')
    plt.xticks(range(len(all_qualities)), all_quality_labels, rotation=45, ha='right')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{height:.3f}', ha='center', va='bottom', fontsize=8)
    
    # 4. Model Usage Summary (Bar Chart)
    plt.subplot(3, 3, 4)
    usage_counts = df['model'].value_counts()
    
    # Create usage data for all models
    all_usage = []
    all_usage_labels = []
    for model in all_models:
        if model in usage_counts.index:
            all_usage.append(usage_counts[model])
        else:
            all_usage.append(0)
        all_usage_labels.append(model.split(':')[-1])
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_usage)))
    bars = plt.bar(range(len(all_usage)), all_usage, color=colors)
    plt.title('Model Usage Count (Benchmark)', fontsize=14, fontweight='bold')
    plt.xlabel('Models')
    plt.ylabel('Number of Tasks')
    plt.xticks(range(len(all_usage)), all_usage_labels, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8)
    
    # 5. Cost vs Quality Scatter Plot
    plt.subplot(3, 3, 5)
    for model in all_models:
        model_data = df[df['model'] == model]
        if not model_data.empty:
            plt.scatter(model_data['estimated_cost'], model_data['quality_score'], 
                       label=model.split(':')[-1], alpha=0.7, s=60)
        else:
            # Plot config values for unused models
            config_cost = router.profiles[model]['cost'] * 0.1
            config_quality = router.profiles[model]['quality']
            plt.scatter(config_cost, config_quality, 
                       label=model.split(':')[-1], alpha=0.5, s=40, marker='x')
    
    plt.title('Cost vs Quality Trade-off', fontsize=14, fontweight='bold')
    plt.xlabel('Estimated Cost ($)')
    plt.ylabel('Quality Score')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3)
    
    # 6. Speed vs Quality Scatter Plot
    plt.subplot(3, 3, 6)
    for model in all_models:
        model_data = df[df['model'] == model]
        if not model_data.empty:
            plt.scatter(model_data['response_time'], model_data['quality_score'], 
                       label=model.split(':')[-1], alpha=0.7, s=60)
        else:
            # Plot config values for unused models
            config_latency = router.profiles[model]['latency']
            config_quality = router.profiles[model]['quality']
            plt.scatter(config_latency, config_quality, 
                       label=model.split(':')[-1], alpha=0.5, s=40, marker='x')
    
    plt.title('Speed vs Quality Trade-off', fontsize=14, fontweight='bold')
    plt.xlabel('Response Time (seconds)')
    plt.ylabel('Quality Score')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.grid(True, alpha=0.3)
    
    # 7. Model Performance Summary Table
    plt.subplot(3, 3, 7)
    plt.axis('off')
    
    # Create summary table
    summary_data = []
    for model in all_models:
        profile = router.profiles[model]
        usage_count = usage_counts.get(model, 0)
        summary_data.append([
            model.split(':')[-1],
            f"${profile['cost']:.3f}",
            f"{profile['latency']:.2f}s",
            f"{profile['quality']:.2f}",
            str(usage_count)
        ])
    
    table = plt.table(cellText=summary_data,
                     colLabels=['Model', 'Cost/1K', 'Latency', 'Quality', 'Used'],
                     cellLoc='center',
                     loc='center',
                     bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    
    # Color code the table
    for i in range(len(summary_data)):
        if summary_data[i][4] != '0':  # If model was used
            for j in range(5):
                table[(i+1, j)].set_facecolor('#e6f3ff')
    
    plt.title('Model Configuration Summary', fontsize=14, fontweight='bold', pad=20)
    
    # 8. Task Category Performance Heatmap
    plt.subplot(3, 3, 8)
    pivot_data = df.pivot_table(values='quality_score', index='model', columns='task_category', aggfunc='mean')
    if not pivot_data.empty:
        im = plt.imshow(pivot_data.values, cmap='RdYlBu_r', aspect='auto')
        plt.title('Quality Score Heatmap by Task Category', fontsize=14, fontweight='bold')
        plt.xlabel('Task Categories')
        plt.ylabel('Models')
        plt.xticks(range(len(pivot_data.columns)), pivot_data.columns, rotation=45)
        plt.yticks(range(len(pivot_data.index)), [m.split(':')[-1] for m in pivot_data.index])
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Quality Score')
        
        # Add text annotations
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                text = plt.text(j, i, f'{pivot_data.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black", fontsize=8)
    
    # 9. Cost Savings Analysis
    plt.subplot(3, 3, 9)
    if not df.empty:
        # Calculate savings vs GPT-4o baseline
        gpt4o_cost = router.profiles.get('openai:gpt-4o', {}).get('cost', 5.0)
        savings_data = []
        savings_labels = []
        
        for model in all_models:
            if model in usage_counts.index and usage_counts[model] > 0:
                model_cost = router.profiles[model]['cost']
                savings_per_task = gpt4o_cost - model_cost
                total_savings = savings_per_task * usage_counts[model]
                savings_data.append(total_savings)
                savings_labels.append(model.split(':')[-1])
        
        if savings_data:
            colors = plt.cm.Greens(np.linspace(0.3, 1, len(savings_data)))
            bars = plt.bar(range(len(savings_data)), savings_data, color=colors)
            plt.title('Cost Savings vs GPT-4o Baseline', fontsize=14, fontweight='bold')
            plt.xlabel('Models')
            plt.ylabel('Total Savings ($)')
            plt.xticks(range(len(savings_data)), savings_labels, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'${height:.2f}', ha='center', va='bottom', fontsize=8)
        else:
            plt.text(0.5, 0.5, 'No cost savings data\n(All models unused)', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('Cost Savings vs GPT-4o Baseline', fontsize=14, fontweight='bold')
    else:
        plt.text(0.5, 0.5, 'No benchmark data available', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('Cost Savings vs GPT-4o Baseline', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    chart_filename = f"agentsiq_benchmark_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    print(f"📊 Performance charts saved to: {chart_filename}")
    
    # Show the plot
    plt.show()

def run_original_benchmark():
    """Run the original benchmark for comparison"""
    print("\n🔄 Running Original Benchmark for Comparison")
    print("=" * 50)
    
    researcher = Agent("Researcher", "Finds information", "openai:gpt-4o-mini", ["retrieval"])
    analyst = Agent("Analyst", "Summarizes info", "anthropic:claude-3-haiku", ["summarize"])
    collab = Collab([researcher, analyst], {"retrieval": lambda _: "[retrieval] ok", "summarize": lambda _: "[summary] ok"})
    
    tasks = [
        "Summarize the key ideas of retrieval-augmented generation in 5 bullet points.",
        "Write a tiny Python function to reverse a list and explain its complexity.",
        "Give a TL;DR of multi-agent coordination strategies.",
        "Draft a simple regex to capture email addresses and explain edge cases.",
    ]
    
    for t in tasks:
        _ = collab.run(t)
        time.sleep(0.1)
    
    decs = latest_decisions(100)
    by_model = {}
    cost_total = 0.0
    saved_vs_gpt4o = 0.0
    
    for d in decs:
        if d.get("strategy") != "smart":
            continue
        m = d.get("chosen")
        by_model[m] = by_model.get(m, 0) + 1
        cost_total += float(d.get("est_cost_chosen") or 0.0)
        saved_vs_gpt4o += float(d.get("est_cost_saved_vs_gpt4o") or 0.0)
    
    print("\nBENCHMARK SUMMARY")
    print("==================")
    print("Model usage:", json.dumps(by_model, indent=2))
    print("Estimated total cost: $%.4f" % cost_total)
    print("Estimated saved vs GPT-4o baseline: $%.4f" % saved_vs_gpt4o)
    print("\nOpen /decisions for per-task rationale.")

def run():
    """Main benchmark runner with options"""
    print("🎯 AgentsIQ Intelligent Model Selection Benchmark")
    print("=" * 60)
    print("Choose benchmark type:")
    print("1. Comprehensive Model Comparison (NEW)")
    print("2. Original Benchmark")
    print("3. Both")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            run_comprehensive_benchmark()
        elif choice == "2":
            run_original_benchmark()
        elif choice == "3":
            run_comprehensive_benchmark()
            run_original_benchmark()
        else:
            print("Invalid choice. Running comprehensive benchmark...")
            run_comprehensive_benchmark()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Benchmark interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error running benchmark: {e}")
        print("Falling back to original benchmark...")
        run_original_benchmark()

if __name__ == "__main__":
    run()
