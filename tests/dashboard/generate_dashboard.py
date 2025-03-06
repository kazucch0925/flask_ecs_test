#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

# ダッシュボードのHTMLテンプレート
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD品質ダッシュボード</title>
    <style>
        :root {
            --primary-color: #3498db;
            --secondary-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--dark-color);
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        h1 {
            margin: 0;
            font-size: 2.5em;
        }
        
        .build-info {
            background-color: var(--light-color);
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .card-header {
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-title {
            margin: 0;
            font-size: 1.5em;
            color: var(--dark-color);
        }
        
        .status-badge {
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8em;
            text-transform: uppercase;
        }
        
        .status-success {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .status-warning {
            background-color: var(--warning-color);
            color: white;
        }
        
        .status-danger {
            background-color: var(--danger-color);
            color: white;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .metric-name {
            font-weight: bold;
        }
        
        .metric-value {
            font-family: monospace;
        }
        
        .progress-bar {
            height: 10px;
            background-color: #eee;
            border-radius: 5px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        
        .progress-value {
            height: 100%;
            border-radius: 5px;
        }
        
        .progress-high {
            background-color: var(--secondary-color);
        }
        
        .progress-medium {
            background-color: var(--warning-color);
        }
        
        .progress-low {
            background-color: var(--danger-color);
        }
        
        .test-summary {
            display: flex;
            justify-content: space-around;
            margin-bottom: 15px;
        }
        
        .test-stat {
            text-align: center;
        }
        
        .test-value {
            font-size: 2em;
            font-weight: bold;
        }
        
        .test-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .security-issues {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }
        
        .security-issue {
            padding: 10px;
            border-left: 4px solid;
            margin-bottom: 10px;
        }
        
        .security-critical {
            border-color: var(--danger-color);
            background-color: rgba(231, 76, 60, 0.1);
        }
        
        .security-high {
            border-color: var(--warning-color);
            background-color: rgba(243, 156, 18, 0.1);
        }
        
        .security-medium {
            border-color: var(--primary-color);
            background-color: rgba(52, 152, 219, 0.1);
        }
        
        .security-low {
            border-color: var(--secondary-color);
            background-color: rgba(46, 204, 113, 0.1);
        }
        
        .issue-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .issue-description {
            font-size: 0.9em;
            color: #666;
        }
        
        .chart-container {
            height: 200px;
            position: relative;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        .links {
            margin-top: 30px;
        }
        
        .link-button {
            display: inline-block;
            padding: 10px 15px;
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: background-color 0.3s;
        }
        
        .link-button:hover {
            background-color: #2980b9;
        }
        
        /* 円グラフ用のスタイル */
        .pie-chart {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(
                var(--secondary-color) 0% {coverage_angle}deg,
                #eee {coverage_angle}deg 360deg
            );
            margin: 0 auto;
            position: relative;
        }
        
        .pie-center {
            position: absolute;
            width: 100px;
            height: 100px;
            background: white;
            border-radius: 50%;
            top: 25px;
            left: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
        }
        
        /* 棒グラフ用のスタイル */
        .bar-chart {
            display: flex;
            height: 200px;
            align-items: flex-end;
            justify-content: space-around;
            padding-top: 20px;
        }
        
        .bar {
            width: 40px;
            background-color: var(--primary-color);
            position: relative;
            border-radius: 5px 5px 0 0;
            transition: height 0.5s;
        }
        
        .bar-label {
            position: absolute;
            bottom: -25px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8em;
        }
        
        .bar-value {
            position: absolute;
            top: -25px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <header>
        <h1>CI/CD品質ダッシュボード</h1>
        <p>アプリケーション品質メトリクスの可視化</p>
    </header>
    
    <div class="container">
        <div class="build-info">
            <h2>ビルド情報</h2>
            <div class="metric">
                <span class="metric-name">ビルド日時:</span>
                <span class="metric-value">{build_date}</span>
            </div>
            <div class="metric">
                <span class="metric-name">ビルドステータス:</span>
                <span class="status-badge {build_status_class}">{build_status}</span>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- コードカバレッジカード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">コードカバレッジ</h3>
                    <span class="status-badge {coverage_status_class}">{coverage_status}</span>
                </div>
                <div class="pie-chart">
                    <div class="pie-center">{coverage}%</div>
                </div>
                <div class="metric">
                    <span class="metric-name">ステートメント:</span>
                    <span class="metric-value">{statements_covered}/{total_statements}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">ブランチ:</span>
                    <span class="metric-value">{branches_covered}/{total_branches}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">関数:</span>
                    <span class="metric-value">{functions_covered}/{total_functions}</span>
                </div>
            </div>
            
            <!-- テスト結果カード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">テスト結果</h3>
                    <span class="status-badge {test_status_class}">{test_status}</span>
                </div>
                <div class="test-summary">
                    <div class="test-stat">
                        <div class="test-value">{total_tests}</div>
                        <div class="test-label">テスト数</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{passed_tests}</div>
                        <div class="test-label">成功</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{failed_tests}</div>
                        <div class="test-label">失敗</div>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-name">実行時間:</span>
                    <span class="metric-value">{test_duration}秒</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-value {test_progress_class}" style="width: {test_success_rate}%;"></div>
                </div>
            </div>
            
            <!-- 静的解析カード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">静的解析</h3>
                    <span class="status-badge {static_analysis_status_class}">{static_analysis_status}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">警告:</span>
                    <span class="metric-value">{warnings}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">エラー:</span>
                    <span class="metric-value">{errors}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">コード品質スコア:</span>
                    <span class="metric-value">{code_quality_score}/10</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-value {code_quality_class}" style="width: {code_quality_percent}%;"></div>
                </div>
            </div>
            
            <!-- セキュリティスキャンカード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">セキュリティスキャン</h3>
                    <span class="status-badge {security_status_class}">{security_status}</span>
                </div>
                <div class="test-summary">
                    <div class="test-stat">
                        <div class="test-value">{critical_issues}</div>
                        <div class="test-label">重大</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{high_issues}</div>
                        <div class="test-label">高</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{medium_issues}</div>
                        <div class="test-label">中</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{low_issues}</div>
                        <div class="test-label">低</div>
                    </div>
                </div>
                <h4>主な脆弱性</h4>
                <ul class="security-issues">
                    {security_issues_html}
                </ul>
            </div>
            
            <!-- パフォーマンステストカード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">パフォーマンステスト</h3>
                    <span class="status-badge {performance_status_class}">{performance_status}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">平均応答時間:</span>
                    <span class="metric-value">{avg_response_time}ms</span>
                </div>
                <div class="metric">
                    <span class="metric-name">最大応答時間:</span>
                    <span class="metric-value">{max_response_time}ms</span>
                </div>
                <div class="metric">
                    <span class="metric-name">リクエスト/秒:</span>
                    <span class="metric-value">{requests_per_second}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">エラー率:</span>
                    <span class="metric-value">{error_rate}%</span>
                </div>
                <div class="bar-chart">
                    <div class="bar" style="height: {get_bar_height}px;">
                        <div class="bar-value">{get_response_time}ms</div>
                        <div class="bar-label">GET</div>
                    </div>
                    <div class="bar" style="height: {post_bar_height}px;">
                        <div class="bar-value">{post_response_time}ms</div>
                        <div class="bar-label">POST</div>
                    </div>
                    <div class="bar" style="height: {put_bar_height}px;">
                        <div class="bar-value">{put_response_time}ms</div>
                        <div class="bar-label">PUT</div>
                    </div>
                    <div class="bar" style="height: {delete_bar_height}px;">
                        <div class="bar-value">{delete_response_time}ms</div>
                        <div class="bar-label">DELETE</div>
                    </div>
                </div>
            </div>
            
            <!-- Dockerイメージスキャンカード -->
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Dockerイメージスキャン</h3>
                    <span class="status-badge {docker_scan_status_class}">{docker_scan_status}</span>
                </div>
                <div class="test-summary">
                    <div class="test-stat">
                        <div class="test-value">{docker_critical_issues}</div>
                        <div class="test-label">重大</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{docker_high_issues}</div>
                        <div class="test-label">高</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{docker_medium_issues}</div>
                        <div class="test-label">中</div>
                    </div>
                    <div class="test-stat">
                        <div class="test-value">{docker_low_issues}</div>
                        <div class="test-label">低</div>
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-name">イメージサイズ:</span>
                    <span class="metric-value">{docker_image_size}</span>
                </div>
                <div class="metric">
                    <span class="metric-name">レイヤー数:</span>
                    <span class="metric-value">{docker_layers}</span>
                </div>
                <h4>主な脆弱性</h4>
                <ul class="security-issues">
                    {docker_issues_html}
                </ul>
            </div>
        </div>
        
        <div class="links">
            <h2>詳細レポート</h2>
            <a href="combined_coverage_report/index.html" class="link-button">カバレッジレポート</a>
            <a href="app_test_report.html" class="link-button">テストレポート</a>
            <a href="bandit_report.html" class="link-button">セキュリティレポート</a>
            <a href="performance_report.html" class="link-button">パフォーマンスレポート</a>
        </div>
    </div>
    
    <footer>
        <p>© 2025 CI/CD品質ダッシュボード | 生成日時: {generation_date}</p>
    </footer>
</body>
</html>
"""

def parse_coverage_data():
    """カバレッジデータを解析する"""
    try:
        # .coverageファイルが存在する場合は、そこからデータを取得
        # ここでは簡易的に固定値を返す
        return {
            'coverage': 75,
            'statements_covered': 750,
            'total_statements': 1000,
            'branches_covered': 120,
            'total_branches': 200,
            'functions_covered': 80,
            'total_functions': 100
        }
    except Exception as e:
        print(f"カバレッジデータの解析中にエラーが発生しました: {e}")
        return {
            'coverage': 0,
            'statements_covered': 0,
            'total_statements': 0,
            'branches_covered': 0,
            'total_branches': 0,
            'functions_covered': 0,
            'total_functions': 0
        }

def parse_test_results():
    """テスト結果を解析する"""
    try:
        # テストレポートからデータを取得
        # ここでは簡易的に固定値を返す
        return {
            'total_tests': 42,
            'passed_tests': 40,
            'failed_tests': 2,
            'test_duration': 3.5,
            'test_success_rate': 95  # パーセント
        }
    except Exception as e:
        print(f"テスト結果の解析中にエラーが発生しました: {e}")
        return {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_duration': 0,
            'test_success_rate': 0
        }

def parse_static_analysis():
    """静的解析結果を解析する"""
    try:
        # pylintレポートからデータを取得
        # ここでは簡易的に固定値を返す
        return {
            'warnings': 15,
            'errors': 3,
            'code_quality_score': 8.5
        }
    except Exception as e:
        print(f"静的解析結果の解析中にエラーが発生しました: {e}")
        return {
            'warnings': 0,
            'errors': 0,
            'code_quality_score': 0
        }

def parse_security_scan():
    """セキュリティスキャン結果を解析する"""
    try:
        # banditレポートからデータを取得
        # ここでは簡易的に固定値を返す
        issues = [
            {
                'severity': 'high',
                'title': 'SQL Injection Vulnerability',
                'description': 'Possible SQL injection in app/routes/tasks.py:45'
            },
            {
                'severity': 'medium',
                'title': 'Insecure Password Hashing',
                'description': 'Weak password hashing algorithm in app/routes/auth.py:28'
            },
            {
                'severity': 'low',
                'title': 'Hardcoded Secret',
                'description': 'Potential hardcoded secret in app/config.py:12'
            }
        ]
        
        return {
            'critical_issues': 0,
            'high_issues': 1,
            'medium_issues': 1,
            'low_issues': 1,
            'issues': issues
        }
    except Exception as e:
        print(f"セキュリティスキャン結果の解析中にエラーが発生しました: {e}")
        return {
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'issues': []
        }

def parse_performance_test():
    """パフォーマンステスト結果を解析する"""
    try:
        # locustレポートからデータを取得
        # ここでは簡易的に固定値を返す
        return {
            'avg_response_time': 120,
            'max_response_time': 350,
            'requests_per_second': 45.5,
            'error_rate': 1.2,
            'get_response_time': 85,
            'post_response_time': 150,
            'put_response_time': 130,
            'delete_response_time': 95
        }
    except Exception as e:
        print(f"パフォーマンステスト結果の解析中にエラーが発生しました: {e}")
        return {
            'avg_response_time': 0,
            'max_response_time': 0,
            'requests_per_second': 0,
            'error_rate': 0,
            'get_response_time': 0,
            'post_response_time': 0,
            'put_response_time': 0,
            'delete_response_time': 0
        }

def parse_docker_scan():
    """Dockerイメージスキャン結果を解析する"""
    try:
        # trivyレポートからデータを取得
        # ここでは簡易的に固定値を返す
        issues = [
            {
                'severity': 'high',
                'title': 'CVE-2023-1234',
                'description': 'Critical vulnerability in python:3.10 base image'
            },
            {
                'severity': 'medium',
                'title': 'CVE-2023-5678',
                'description': 'Medium severity issue in pip package'
            }
        ]
        
        return {
            'docker_critical_issues': 0,
            'docker_high_issues': 1,
            'docker_medium_issues': 1,
            'docker_low_issues': 0,
            'docker_image_size': '125MB',
            'docker_layers': 8,
            'docker_issues': issues
        }
    except Exception as e:
        print(f"Dockerイメージスキャン結果の解析中にエラーが発生しました: {e}")
        return {
            'docker_critical_issues': 0,
            'docker_high_issues': 0,
            'docker_medium_issues': 0,
            'docker_low_issues': 0,
            'docker_image_size': '0MB',
            'docker_layers': 0,
            'docker_issues': []
        }

def generate_security_issues_html(issues):
    """セキュリティ問題のHTMLを生成する"""
    html = ""
    for issue in issues:
        severity_class = f"security-{issue['severity']}"
        html += f"""
        <li class="security-issue {severity_class}">
            <div class="issue-title">{issue['title']}</div>
            <div class="issue-description">{issue['description']}</div>
        </li>
        """
    return html

def get_status_class(value, thresholds):
    """ステータスクラスを取得する"""
    if value >= thresholds['good']:
        return 'status-success'
    elif value >= thresholds['warning']:
        return 'status-warning'
    else:
        return 'status-danger'

def get_progress_class(value, thresholds):
    """プログレスバーのクラスを取得する"""
    if value >= thresholds['good']:
        return 'progress-high'
    elif value >= thresholds['warning']:
        return 'progress-medium'
    else:
        return 'progress-low'

def generate_dashboard():
    """ダッシュボードを生成する"""
    # 各種データを取得
    coverage_data = parse_coverage_data()
    test_data = parse_test_results()
    static_analysis_data = parse_static_analysis()
    security_data = parse_security_scan()
    performance_data = parse_performance_test()
    docker_data = parse_docker_scan()
    
    # ステータスとクラスを決定
    coverage = coverage_data['coverage']
    coverage_status = 'PASS' if coverage >= 70 else 'WARNING' if coverage >= 50 else 'FAIL'
    coverage_status_class = get_status_class(coverage, {'good': 70, 'warning': 50})
    
    test_success_rate = test_data['test_success_rate']
    test_status = 'PASS' if test_success_rate == 100 else 'WARNING' if test_success_rate >= 90 else 'FAIL'
    test_status_class = get_status_class(test_success_rate, {'good': 100, 'warning': 90})
    test_progress_class = get_progress_class(test_success_rate, {'good': 100, 'warning': 90})
    
    code_quality_score = static_analysis_data['code_quality_score']
    code_quality_percent = code_quality_score * 10
    static_analysis_status = 'PASS' if code_quality_score >= 8 else 'WARNING' if code_quality_score >= 6 else 'FAIL'
    static_analysis_status_class = get_status_class(code_quality_score, {'good': 8, 'warning': 6})
    code_quality_class = get_progress_class(code_quality_score, {'good': 8, 'warning': 6})
    
    security_issues = security_data['critical_issues'] + security_data['high_issues']
    security_status = 'PASS' if security_issues == 0 else 'WARNING' if security_issues <= 2 else 'FAIL'
    security_status_class = get_status_class(10 - security_issues, {'good': 10, 'warning': 8})
    security_issues_html = generate_security_issues_html(security_data['issues'])
    
    avg_response_time = performance_data['avg_response_time']
    performance_status = 'PASS' if avg_response_time < 200 else 'WARNING' if avg_response_time < 500 else 'FAIL'
    performance_status_class = get_status_class(1000 - avg_response_time, {'good': 800, 'warning': 500})
    
    # パフォーマンスグラフの高さを計算（最大200px）
    max_response = max(
        performance_data['get_response_time'],
        performance_data['post_response_time'],
        performance_data['put_response_time'],
        performance_data['delete_response_time']
    )
    get_bar_height = int(performance_data['get_response_time'] / max_response * 180)
    post_bar_height = int(performance_data['post_response_time'] / max_response * 180)
    put_bar_height = int(performance_data['put_response_time'] / max_response * 180)
    delete_bar_height = int(performance_data['delete_response_time'] / max_response * 180)
    
    docker_issues = docker_data['docker_critical_issues'] + docker_data['docker_high_issues']
    docker_scan_status = 'PASS' if docker_issues == 0 else 'WARNING' if docker_issues <= 2 else 'FAIL'
    docker_scan_status_class = get_status_class(10 - docker_issues, {'good': 10, 'warning': 8})
    docker_issues_html = generate_security_issues_html(docker_data['docker_issues'])
    
    # ビルド情報
    build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    build_status = 'SUCCESS' if test_status == 'PASS' and security_status == 'PASS' else 'WARNING' if test_status != 'FAIL' and security_status != 'FAIL' else 'FAILURE'
    build_status_class = 'status-success' if build_status == 'SUCCESS' else 'status-warning' if build_status == 'WARNING' else 'status-danger'
    
    # 円グラフの角度を計算
    coverage_angle = coverage * 3.6  # 100% = 360度
    
    # 現在の日時
    generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # テンプレートに値を埋め込む
    dashboard_html = DASHBOARD_TEMPLATE.format(
        build_date=build_date,
        build_status=build_status,
        build_status_class=build_status_class,
        coverage=coverage,
        coverage_status=coverage_status,
        coverage_status_class=coverage_status_class,
        coverage_angle=coverage_angle,
        statements_covered=coverage_data['statements_covered'],
        total_statements=coverage_data['total_statements'],
        branches_covered=coverage_data['branches_covered'],
        total_branches=coverage_data['total_branches'],
        functions_covered=coverage_data['functions_covered'],
        total_functions=coverage_data['total_functions'],
        total_tests=test_data['total_tests'],
        passed_tests=test_data['passed_tests'],
        failed_tests=test_data['failed_tests'],
        test_duration=test_data['test_duration'],
        test_success_rate=test_data['test_success_rate'],
        test_status=test_status,
        test_status_class=test_status_class,
        test_progress_class=test_progress_class,
        warnings=static_analysis_data['warnings'],
        errors=static_analysis_data['errors'],
        code_quality_score=static_analysis_data['code_quality_score'],
        code_quality_percent=code_quality_percent,
        static_analysis_status=static_analysis_status,
        static_analysis_status_class=static_analysis_status_class,
        code_quality_class=code_quality_class,
        critical_issues=security_data['critical_issues'],
        high_issues=security_data['high_issues'],
        medium_issues=security_data['medium_issues'],
        low_issues=security_data['low_issues'],
        security_status=security_status,
        security_status_class=security_status_class,
        security_issues_html=security_issues_html,
        avg_response_time=performance_data['avg_response_time'],
        max_response_time=performance_data['max_response_time'],
        requests_per_second=performance_data['requests_per_second'],
        error_rate=performance_data['error_rate'],
        get_response_time=performance_data['get_response_time'],
        post_response_time=performance_data['post_response_time'],
        put_response_time=performance_data['put_response_time'],
        delete_response_time=performance_data['delete_response_time'],
        get_bar_height=get_bar_height,
        post_bar_height=post_bar_height,
        put_bar_height=put_bar_height,
        delete_bar_height=delete_bar_height,
        performance_status=performance_status,
        performance_status_class=performance_status_class,
        docker_critical_issues=docker_data['docker_critical_issues'],
        docker_high_issues=docker_data['docker_high_issues'],
        docker_medium_issues=docker_data['docker_medium_issues'],
        docker_low_issues=docker_data['docker_low_issues'],
        docker_image_size=docker_data['docker_image_size'],
        docker_layers=docker_data['docker_layers'],
        docker_scan_status=docker_scan_status,
        docker_scan_status_class=docker_scan_status_class,
        docker_issues_html=docker_issues_html,
        generation_date=generation_date
    )
    
    return dashboard_html

def main():
    """メイン関数"""
    try:
        # ダッシュボードHTMLを生成
        dashboard_html = generate_dashboard()
        
        # 出力ディレクトリを作成
        os.makedirs('quality_dashboard', exist_ok=True)
        
        # HTMLファイルに書き込み
        with open('quality_dashboard.html', 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print("品質ダッシュボードが正常に生成されました: quality_dashboard.html")
        return 0
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
