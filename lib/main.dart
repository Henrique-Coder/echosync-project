import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'YouTube Video Info',
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
  String _responseJson = '';

  Future<void> _extractVideoInfo() async {
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
        _responseJson = _formatJson(response.body);
      });
    } else {
      setState(() {
        _responseJson = 'ID not found';
      });
    }
  }

  String _formatJson(String jsonString) {
    final dynamic parsedJson = json.decode(jsonString);
    final JsonEncoder encoder = JsonEncoder.withIndent('  ');
    return encoder.convert(parsedJson);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('YouTube Video Info'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Expanded(
              child: TextField(
                controller: _urlController,
                decoration: InputDecoration(
                  labelText: 'Enter YouTube video URL',
                ),
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
            Expanded(
              child: SingleChildScrollView(
                child: Text(
                  'JSON Response:\n$_responseJson',
                  style: TextStyle(fontSize: 18.0),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
