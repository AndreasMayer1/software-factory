// Complexity-metric analyzer for Dart sources.
//
// Walks each input path (file or directory), parses every .dart file with
// the analyzer package's parseFile() helper, and computes four metrics per
// FunctionDeclaration / MethodDeclaration / ConstructorDeclaration:
//
//   - cyclomatic    1 + count of branching nodes
//   - parameters    formal parameter list length (positional + named)
//   - sloc          source lines in the function body, blank-and-
//                   standalone-comment lines subtracted
//   - max_nesting   maximum nesting depth of control-flow statements
//                   (NOT widget composition / map literals — see
//                   REQ-PROC-046 AC-02 clarification)
//
// Emits a single JSON document to stdout:
//
//   {"version": 1,
//    "files": [
//      {"path": "lib/foo.dart",
//       "functions": [
//         {"name": "doThing", "line": 42,
//          "cyclomatic": 3, "parameters": 2,
//          "sloc": 18, "max_nesting": 2}
//       ]}
//     ]}
//
// Exit codes: 0 on success, 2 on parser error (printed to stderr).

import 'dart:convert';
import 'dart:io';

import 'package:analyzer/dart/analysis/features.dart';
import 'package:analyzer/dart/analysis/utilities.dart';
import 'package:analyzer/dart/ast/ast.dart';
import 'package:analyzer/dart/ast/visitor.dart';
import 'package:analyzer/source/line_info.dart';
import 'package:path/path.dart' as p;

void main(List<String> args) {
  if (args.isEmpty) {
    stderr.writeln('usage: complexity_analyzer <path> [<path>...]');
    exit(2);
  }

  final files = <File>[];
  for (final arg in args) {
    final entity = FileSystemEntity.typeSync(arg);
    if (entity == FileSystemEntityType.file) {
      if (arg.endsWith('.dart')) files.add(File(arg));
    } else if (entity == FileSystemEntityType.directory) {
      for (final f in Directory(arg)
          .listSync(recursive: true, followLinks: false)
          .whereType<File>()) {
        if (f.path.endsWith('.dart') &&
            !f.path.endsWith('.g.dart') &&
            !f.path.endsWith('.freezed.dart')) {
          files.add(f);
        }
      }
    }
  }

  final out = <String, Object?>{'version': 1, 'files': <Object?>[]};
  final fileList = out['files']! as List<Object?>;

  for (final file in files) {
    try {
      final parse = parseFile(
        path: p.normalize(p.absolute(file.path)),
        featureSet: FeatureSet.latestLanguageVersion(),
      );
      if (parse.errors.isNotEmpty) {
        stderr.writeln(
          'WARN: ${file.path}: ${parse.errors.length} parse error(s); skipped.',
        );
        continue;
      }
      final visitor = _ComplexityVisitor(parse.lineInfo);
      parse.unit.accept(visitor);
      if (visitor.functions.isNotEmpty) {
        fileList.add(<String, Object?>{
          'path': p.normalize(p.absolute(file.path)),
          'functions': visitor.functions,
        });
      }
    } catch (e, st) {
      stderr.writeln('ERROR parsing ${file.path}: $e');
      stderr.writeln(st);
      exit(2);
    }
  }

  stdout.writeln(const JsonEncoder.withIndent('  ').convert(out));
}

class _ComplexityVisitor extends RecursiveAstVisitor<void> {
  _ComplexityVisitor(this._lineInfo);

  final LineInfo _lineInfo;
  final List<Map<String, Object?>> functions = [];

  void _record(String name, int offset, FormalParameterList? params,
      FunctionBody body, {String kind = 'function'}) {
    final line = _lineInfo.getLocation(offset).lineNumber;
    final paramCount = params?.parameters.length ?? 0;
    final m = _BodyMetrics(_lineInfo)..visitFunctionBody(body);
    functions.add({
      'name': name,
      'line': line,
      'kind': kind,
      'cyclomatic': m.cyclomatic,
      'parameters': paramCount,
      'sloc': m.sloc,
      'max_nesting': m.maxNesting,
    });
  }

  @override
  void visitFunctionDeclaration(FunctionDeclaration node) {
    _record(node.name.lexeme, node.offset,
        node.functionExpression.parameters, node.functionExpression.body);
    super.visitFunctionDeclaration(node);
  }

  @override
  void visitMethodDeclaration(MethodDeclaration node) {
    _record(node.name.lexeme, node.offset, node.parameters, node.body,
        kind: 'method');
    super.visitMethodDeclaration(node);
  }

  @override
  void visitConstructorDeclaration(ConstructorDeclaration node) {
    final parent = node.parent;
    String containerName = '<ctor>';
    if (parent is ClassDeclaration) {
      containerName = parent.name.lexeme;
    } else if (parent is EnumDeclaration) {
      containerName = parent.name.lexeme;
    } else if (parent is ExtensionTypeDeclaration) {
      containerName = parent.name.lexeme;
    }
    final n = node.name?.lexeme ?? containerName;
    _record(n, node.offset, node.parameters, node.body, kind: 'constructor');
    super.visitConstructorDeclaration(node);
  }
}

class _BodyMetrics {
  _BodyMetrics(this._lineInfo);
  final LineInfo _lineInfo;

  int cyclomatic = 1;
  int sloc = 0;
  int maxNesting = 0;

  void visitFunctionBody(FunctionBody body) {
    if (body is BlockFunctionBody) {
      _computeSloc(body.block.leftBracket.offset, body.block.rightBracket.offset);
    } else if (body is ExpressionFunctionBody) {
      sloc = 1;
    } else {
      sloc = 0;
    }
    final visitor = _BranchVisitor()..visitBody(body);
    cyclomatic = 1 + visitor.branchCount;
    maxNesting = visitor.maxNesting;
  }

  void _computeSloc(int openOffset, int closeOffset) {
    final openLine = _lineInfo.getLocation(openOffset).lineNumber;
    final closeLine = _lineInfo.getLocation(closeOffset).lineNumber;
    sloc = (closeLine - openLine - 1).clamp(0, 1 << 30);
  }
}

class _BranchVisitor extends RecursiveAstVisitor<void> {
  int branchCount = 0;
  int _currentNesting = 0;
  int maxNesting = 0;

  void visitBody(FunctionBody body) {
    body.accept(this);
  }

  void _enter() {
    _currentNesting++;
    if (_currentNesting > maxNesting) maxNesting = _currentNesting;
  }

  void _exit() => _currentNesting--;

  @override
  void visitIfStatement(IfStatement node) {
    branchCount++;
    _enter();
    super.visitIfStatement(node);
    _exit();
  }

  @override
  void visitForStatement(ForStatement node) {
    branchCount++;
    _enter();
    super.visitForStatement(node);
    _exit();
  }

  @override
  void visitWhileStatement(WhileStatement node) {
    branchCount++;
    _enter();
    super.visitWhileStatement(node);
    _exit();
  }

  @override
  void visitDoStatement(DoStatement node) {
    branchCount++;
    _enter();
    super.visitDoStatement(node);
    _exit();
  }

  @override
  void visitSwitchStatement(SwitchStatement node) {
    _enter();
    super.visitSwitchStatement(node);
    _exit();
  }

  @override
  void visitSwitchCase(SwitchCase node) {
    branchCount++;
    super.visitSwitchCase(node);
  }

  @override
  void visitCatchClause(CatchClause node) {
    branchCount++;
    super.visitCatchClause(node);
  }

  @override
  void visitConditionalExpression(ConditionalExpression node) {
    branchCount++;
    super.visitConditionalExpression(node);
  }

  @override
  void visitBinaryExpression(BinaryExpression node) {
    if (node.operator.lexeme == '&&' || node.operator.lexeme == '||') {
      branchCount++;
    }
    super.visitBinaryExpression(node);
  }
}
