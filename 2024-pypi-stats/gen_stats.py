#!/usr/bin/env python

from pathlib import Path
import wlc.config
import requests
import json
import time
import pprint
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
import seaborn as sns


WAIT_API_CALL=1
config_path = Path("~/.config/weblate").expanduser()
current_dir_path = Path(__file__).resolve().parent
cache_json_file = current_dir_path.joinpath(".weblate.cache.json")

def get_data_from_weblate():
    results = []
    # load cache
    if cache_json_file.exists():
        print("get data from cache")
        return json.load(open(cache_json_file))
    config = wlc.config.WeblateConfig()
    config.load(path=config_path)
    api_url, api_key = config.get_url_key()
    print(api_url)
    print(api_key)
    headers = {
        "Accept":"application/json",
        "Content-Type":"application/json",
        "Authorization" : "Token " + api_key,
    }
    request_url = api_url + "translations/pypa/warehouse/ko/changes/"
    while request_url:
        response = requests.get(request_url).json()
        if "results" in response:
            results.extend(response["results"])
        if "next" in response:
            request_url = response['next']
        time.sleep(WAIT_API_CALL)
    # dump to cache file
    json.dump(results, open(cache_json_file,'w'))
    return results

def prepare_activity_dataset(data):
    activity_dataset = []
    for item in data:
        if item["user"] is not None:
            user = item["user"].split("/")[-2]
            activity_dataset.append(
                {
                    "user" : user,
                    "timestamp" : item["timestamp"]
                }
            )
    return activity_dataset

def generate_activity_chart(data):
    # 이모지 폰트 설정 (Mac용)
    emoji_font = font_manager.FontProperties(fname='/System/Library/Fonts/Apple Color Emoji.ttc', size=18)
    # rcParams['font.family'] = 'Apple Color Emoji'
    # '/System/Library/Fonts/Apple Color Emoji.ttc'

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Count activities per user
    rank_df = df.groupby('user').size().reset_index(name='activity_count').sort_values(by='activity_count', ascending=False)

    # Count activities per user and filter top 10
    rank_df = (
        df.groupby('user')
        .size()
        .reset_index(name='activity_count')
        .sort_values(by='activity_count', ascending=False)
        .head(10)  # 상위 10명만 선택
    )
    rank_df_all = (
        df.groupby('user')
        .size()
        .reset_index(name='activity_count')
        .sort_values(by='activity_count', ascending=False)
    )



    # 텍스트 테이블로 출력
    print("ID\tActivity Count")
    print("-" * 30)
    for index, row in rank_df_all.iterrows():
        print(f"{row['user']:<15}{row['activity_count']:>5}")

    # Plot Bar Chart
    plt.figure(figsize=(10, 6))

    # Plot add font
    # plt.rcParams['font.family'] = emoji_font_prop.get_family()

    bars = plt.bar(rank_df['user'], rank_df['activity_count'], color='gold', edgecolor='black')


    # Add title and labels
    plt.title('User Activity Ranking', fontsize=16)
    plt.ylabel('Activity Count', fontsize=12)
    plt.xlabel('User', fontsize=12)

    # dose not work with font loading issue
    # # Add trophy graphic for the top user
    # for i, bar in enumerate(bars):
    #     if i == 0:  # Highlight the top user with a trophy
    #         #plt.annote('🏆', (bar.get_x() + bar.get_width() / 2, bar.get_height() - 1), size=18)
    #         plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 1, '🏆', 
    #                  ha='center', va='bottom', fontsize=18, fontproperties=emoji_font)

    # Customize ticks and grid
    plt.xticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout and show plot
    # plt.tight_layout()
    # plt.show()
    # Save the plot as a file
    plt.tight_layout()
    plt.savefig('user_activity_ranking.png', dpi=300, bbox_inches='tight')  # 파일명, 해상도, 여백 설정
    #plt.show()

def plot_and_save_top10_user_activity_trends(data, output_file='top10_user_activity_trends.png'):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Extract the year from the timestamp string
    df['year'] = df['timestamp'].str[:4]

    # Identify rows with invalid years (non-numeric)
    invalid_years = df[~df['year'].str.isnumeric()]

    # Print invalid years if any
    if not invalid_years.empty:
        print("Invalid years detected:")
        print(invalid_years)

    # Drop rows with invalid years
    df = df[df['year'].str.isnumeric()]

    # Convert year to integer
    df['year'] = df['year'].astype(int)

    # Calculate activity counts per user
    user_activity = (
        df.groupby('user')
        .size()
        .reset_index(name='activity_count')
        .sort_values(by='activity_count', ascending=False)
    )

    # Get top 10 users
    top10_users = user_activity.head(10)['user']

    # Filter data for top 10 users
    top10_data = df[df['user'].isin(top10_users)]

    # Aggregate by year and user
    heatmap_data = (
        top10_data.groupby(['year', 'user'])
        .size()
        .unstack(fill_value=0)
        .T  # Transpose for users as rows and years as columns
    )

    # Plot heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,  # Display activity counts
        fmt='d',  # Integer format
        cmap='Blues',  # Color map
        linewidths=0.5,
        linecolor='gray'
    )

    # Add labels and title
    plt.title('Top 10 User Activity Trends (Yearly)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('User', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    # Save the plot to a file
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Heatmap saved to {output_file}")


def main():
    data = get_data_from_weblate()
    activity_data = prepare_activity_dataset(data)
    generate_activity_chart(activity_data)
    plot_and_save_top10_user_activity_trends(activity_data)



if __name__ == '__main__':
    main()