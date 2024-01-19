import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/services.dart' show Clipboard, ClipboardData, SystemChannels, rootBundle;
import 'dart:io' show Platform;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EchoSync Project',
      theme: ThemeData.dark(),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  TextEditingController _urlController = TextEditingController();
  Map<String, dynamic> _responseJson = {};
  String _copiedValue = '';

  Future<void> _extractVideoInfo() async {
    try {
      RegExp regExp = RegExp(
        r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})",
      );

      String? url = _urlController.text;
      RegExpMatch? match = regExp.firstMatch(url!);

      if (match != null) {
        String videoId = match.group(1)!;
        Uri apiUrl = Uri.parse("http://node1.mindwired.com.br:8452/api/wrapper/v1/youtube-video?id=$videoId");
        http.Response response = await http.get(apiUrl);

        setState(() {
          _responseJson = json.decode(response.body) as Map<String, dynamic>;
          _sortMediaData();
          _formatNumericData();
          _formatDuration();
        });
      } else {
        throw Exception('Invalid YouTube URL');
      }
    } catch (e) {
      setState(() {
        _responseJson = {'error': e.toString()};
      });
    }
  }

  void _sortMediaData() {
    if (_responseJson.containsKey('output')) {
      ['video', 'audio', 'subtitles'].forEach((category) {
        _responseJson['output']['data']['media'][category]?.sort((a, b) {
          if (category == 'video') {
            List<String> order = ["4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"];
            int indexA = order.indexOf(a['quality']) ?? order.length;
            int indexB = order.indexOf(b['quality']) ?? order.length;
            return indexA.compareTo(indexB);
          } else if (category == 'audio') {
            int bitrateA = a['bitrate'] ?? 0;
            int bitrateB = b['bitrate'] ?? 0;
            return bitrateB.compareTo(bitrateA);
          } else if (category == 'subtitles') {
            String langA = a['lang'] ?? '';
            String langB = b['lang'] ?? '';
            return langA.compareTo(langB);
          }
          return 0;
        });
      });
    }
  }

  void _formatNumericData() {
    if (_responseJson.containsKey('output')) {
      ['views', 'likes', 'comments'].forEach((key) {
        var infoData = _responseJson['output']['data']['info'];
        if (infoData.containsKey(key) && infoData[key] is num) {
          infoData[key] = _formatNumber(infoData[key]);
        }
      });
    }
  }

  String _formatNumber(num value) {
    String formattedValue = value.toString();
    final RegExp regExp = RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))');
    formattedValue = formattedValue.replaceAllMapped(regExp, (Match match) => '${match[1]},');
    return formattedValue;
  }

  void _formatDuration() {
    if (_responseJson.containsKey('output')) {
      var infoData = _responseJson['output']['data']['info'];
      if (infoData.containsKey('duration') && infoData['duration'] is int) {
        int durationInSeconds = infoData['duration'];
        int hours = durationInSeconds ~/ 3600;
        int minutes = (durationInSeconds % 3600) ~/ 60;
        int seconds = durationInSeconds % 60;
        String formattedDuration = '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
        infoData['duration'] = formattedDuration;
      }
    }
  }

  Widget _buildInfoSection(String title, Map<String, dynamic> data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var entry in data.entries)
          if (entry.value != null && entry.value != '')
            ListTile(
              title: Text(
                '$title${entry.key}',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: GestureDetector(
                onTap: () => title.isEmpty ? _copyToClipboard(entry.value) : null,
                child: Text(
                  '${entry.value}',
                  style: TextStyle(fontWeight: FontWeight.normal),
                ),
              ),
            ),
      ],
    );
  }

  Widget _buildDirectUrlsSection(List<dynamic> items, String category) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var item in items)
          if (item is Map<String, dynamic>)
            ListTile(
              title: GestureDetector(
                onTap: () {
                  if (category == 'General Information') {
                    _copyToClipboard(item['url']);
                  } else {
                    _openUrlInBrowser(item['url']);
                  }
                },
                child: Text(
                  _buildUrlText(item, category),
                  style: TextStyle(color: category == 'General Information' ? Colors.blue : null),
                ),
              ),
            ),
      ],
    );
  }

  String _buildUrlText(Map<String, dynamic> item, String category) {
  if (category == 'Video Direct URLs') {
    String quality = item['quality'] ?? '';
    int bitrate = item['bitrate'] ?? 0;
    String codec = item['codec'] ?? '';
    double sizeInMB = (item['size'] ?? 0) / (1024 * 1024);
    return '$quality - $bitrate kbps - $codec - ${sizeInMB.toStringAsFixed(2)} MB';
  } else if (category == 'Audio Direct URLs') {
    int bitrate = item['bitrate'] ?? 0;
    int sampleRate = item['sample-rate'] ?? 0;
    String codec = item['codec'] ?? '';
    double sizeInMB = (item['size'] ?? 0) / (1024 * 1024);
    return '$bitrate kbps - ${sampleRate / 1000} kHz - $codec - ${sizeInMB.toStringAsFixed(2)} MB';
  } else if (category == 'Subtitle Direct URLs') {
    String lang = item['lang'] ?? '';
    String ext = item['ext'] ?? '';
    return '$lang - $ext';
  }
  return '';
}

  void _copyToClipboard(String value) {
    Clipboard.setData(ClipboardData(text: value));
    setState(() {
      _copiedValue = value;
    });
    Future.delayed(Duration(seconds: 1), () {
      setState(() {
        _copiedValue = '';
      });
    });
  }

  Future<void> _openUrlInBrowser(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('EchoSync Project'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _urlController,
                decoration: InputDecoration(
                  labelText: 'Enter YouTube video URL',
                ),
              ),
              SizedBox(height: 16.0),
              ElevatedButton(
                onPressed: () async {
                  await _extractVideoInfo();
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12.0),
                  child: Text('Get Video Information'),
                ),
              ),
              SizedBox(height: 16.0),
              if (_copiedValue.isNotEmpty)
                Container(
                  color: Colors.green,
                  padding: EdgeInsets.all(8.0),
                  child: Text(
                    'Copied: $_copiedValue',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              if (_responseJson.containsKey('error'))
                Text(
                  'Error: ${_responseJson['error']}',
                  style: TextStyle(fontSize: 18.0),
                ),
              if (_responseJson.containsKey('output'))
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ExpansionTile(
                      title: Text(
                        'General Information',
                        style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                      ),
                      children: [
                        _buildInfoSection('', {
                          'URL': _responseJson['output']['data']['info']['long-url'],
                          'ID': _responseJson['output']['data']['info']['id'],
                          'Title': _responseJson['output']['data']['info']['title'],
                          'Channel ID': _responseJson['output']['data']['info']['channel-id'] ?? '',
                          'Channel name': _responseJson['output']['data']['info']['channel-name'] ?? '',
                          'Duration': _responseJson['output']['data']['info']['duration'],
                          'Views count': _responseJson['output']['data']['info']['views'],
                          'Likes count': _responseJson['output']['data']['info']['likes'],
                          'Comments count': _responseJson['output']['data']['info']['comments'],
                          'Tags': _responseJson['output']['data']['info']['tags']?.join(', ') ?? '',
                          'Categories': _responseJson['output']['data']['info']['categories']?.join(', ') ?? '',
                          'Age restricted': _responseJson['output']['data']['info']['age-restricted'] == true ? 'Yes' : 'No',
                          'Upload date': _responseJson['output']['data']['info']['upload-date']?.toString() ?? '',
                        }),
                      ],
                    ),
                    ExpansionTile(
                      title: Text(
                        'Video URLs',
                        style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                      ),
                      children: [
                        _buildDirectUrlsSection(_responseJson['output']['data']['media']['video'], 'Video Direct URLs'),
                      ],
                    ),
                    ExpansionTile(
                      title: Text(
                        'Audio URLs',
                        style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                      ),
                      children: [
                        _buildDirectUrlsSection(_responseJson['output']['data']['media']['audio'], 'Audio Direct URLs'),
                      ],
                    ),
                    ExpansionTile(
                      title: Text(
                        'Subtitle Direct URLs',
                        style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                      ),
                      children: [
                        _buildDirectUrlsSection(_responseJson['output']['data']['media']['subtitles'], 'Subtitle Direct URLs'),
                      ],
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
