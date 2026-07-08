# YouTube Transcript Skill

## Description
Extract and analyze YouTube video transcripts to gather insights, content analysis, and key takeaways from videos. Perfect for content analysis, research, and learning from video content.

## Features
- ✅ Extract video metadata (title, description, channel info)
- ✅ Retrieve full transcript with timestamps
- ✅ Content analysis and summarization
- ✅ Extract key takeaways and insights
- ✅ Multi-language support
- ✅ Batch processing capabilities

## Usage Examples

### Basic Transcript Extraction
```javascript
// Extract transcript from a YouTube video
const transcript = await youtube_transcript({
  videoUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
});

console.log(transcript);
```

### Advanced Analysis
```javascript
// Get transcript with analysis
const analysis = await youtube_transcript({
  videoUrl: "https://www.youtube.com/watch?v=VIDEO_ID",
  analyze: true,
  extractKeyPoints: true,
  summarize: true
});
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `videoUrl` | string | ✅ | YouTube video URL |
| `analyze` | boolean | ❌ | Perform content analysis |
| `extractKeyPoints` | boolean | ❌ | Extract key takeaways |
| `summarize` | boolean | ❌ | Generate summary |
| `language` | string | ❌ | Preferred language (default: auto) |
| `maxDuration` | number | ❌ | Max video duration to analyze (minutes) |

## Output Structure

### Basic Transcript
```javascript
{
  videoId: "VIDEO_ID",
  title: "Video Title",
  channel: "Channel Name",
  publishedAt: "2023-01-01T00:00:00Z",
  duration: 600, // seconds
  transcript: [
    {
      timestamp: "00:00:00",
      text: "Video transcript text..."
    }
  ],
  totalWords: 2450
}
```

### With Analysis
```javascript
{
  // ... basic transcript data
  analysis: {
    sentiment: "positive",
    topics: ["business", "marketing", "sales"],
    readability: 8.5,
    estimatedReadingTime: "12 min"
  },
  keyPoints: [
    "Key insight 1...",
    "Key insight 2..."
  ],
  summary: "Video summary in 2-3 paragraphs..."
}
```

## Error Handling

- **Invalid URL**: Returns error if URL is not a valid YouTube link
- **Private/Unlisted Videos**: Returns error if transcript is not available
- **No Transcript Available**: Returns empty transcript array
- **Rate Limiting**: Implements retry logic for API limits

## Dependencies
- `youtube-transcript-api` - For transcript extraction
- `axios` - For HTTP requests
- `natural` - For text analysis (optional)

## Performance Notes
- Cache transcripts to avoid repeated API calls
- Process videos under 30 minutes for optimal performance
- Analysis features require additional processing time

## Integration Tips
- Use with content planning workflows
- Combine with video summarization tools
- Great for competitive analysis and market research