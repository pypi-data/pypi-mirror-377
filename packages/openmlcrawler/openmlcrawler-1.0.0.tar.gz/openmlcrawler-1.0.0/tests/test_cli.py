"""
Tests for CLI functionality.
"""

import pytest
from unittest.mock import patch
import sys
from io import StringIO

from openmlcrawler.cli import main, create_parser

class TestCLI:
    """Test CLI functionality."""

    def test_parser_creation(self):
        """Test argument parser creation."""
        parser = create_parser()
        assert parser is not None

        # Test help
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])

    def test_load_command_parsing(self):
        """Test load command parsing."""
        parser = create_parser()

        args = parser.parse_args(['load', 'weather', '--location', 'Delhi'])
        assert args.command == 'load'
        assert args.connector == 'weather'
        assert args.location == 'Delhi'
        assert args.days == 7  # default

    def test_crawl_command_parsing(self):
        """Test crawl command parsing."""
        parser = create_parser()

        args = parser.parse_args(['crawl', 'https://example.com/data.csv'])
        assert args.command == 'crawl'
        assert args.url == 'https://example.com/data.csv'
        assert args.type == 'auto'  # default

    def test_search_command_parsing(self):
        """Test search command parsing."""
        parser = create_parser()

        args = parser.parse_args(['search', 'climate change'])
        assert args.command == 'search'
        assert args.query == 'climate change'
        assert args.max_results == 10  # default

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_no_args(self, mock_stdout):
        """Test main with no arguments."""
        with patch('sys.argv', ['openmlcrawler']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch('openmlcrawler.cli.load_weather_dataset')
    @patch('openmlcrawler.cli.export_dataset')
    def test_load_weather_command(self, mock_export, mock_load):
        """Test load weather command execution."""
        # Mock the dataset loading
        mock_df = type('MockDF', (), {'__len__': lambda self: 10})()
        mock_load.return_value = mock_df

        with patch('sys.argv', ['openmlcrawler', 'load', 'weather', '--location', 'Delhi']):
            result = main()
            assert result == 0
            mock_load.assert_called_once_with(location='Delhi', days=7)

    @patch('openmlcrawler.cli.crawl_and_prepare')
    @patch('openmlcrawler.cli.export_dataset')
    def test_crawl_command(self, mock_export, mock_crawl):
        """Test crawl command execution."""
        # Mock the crawling
        mock_df = type('MockDF', (), {'__len__': lambda self: 5})()
        mock_crawl.return_value = mock_df

        with patch('sys.argv', ['openmlcrawler', 'crawl', 'https://example.com/data.csv']):
            result = main()
            assert result == 0
            mock_crawl.assert_called_once()

    @patch('openmlcrawler.cli.search_open_data')
    @patch('sys.stdout', new_callable=StringIO)
    def test_search_command(self, mock_stdout, mock_search):
        """Test search command execution."""
        mock_search.return_value = [
            {
                'title': 'Test Dataset',
                'description': 'A test dataset',
                'url': 'https://example.com',
                'source': 'test'
            }
        ]

        with patch('sys.argv', ['openmlcrawler', 'search', 'test query']):
            result = main()
            assert result == 0
            mock_search.assert_called_once_with('test query', 10)

            output = mock_stdout.getvalue()
            assert 'Test Dataset' in output
            assert 'https://example.com' in output

if __name__ == '__main__':
    pytest.main([__file__])