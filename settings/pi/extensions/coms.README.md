Example usage, start two pi instances that communicate together:

```
pi -e ~/dotagents/settings/pi/extensions/coms.ts \
--coms-name "dar-agent" \
--purpose "Extract Yoplai orchestrator extension feature into dar project" \
--project "Orchestrator Extraction"
```

```
pi -e ~/dotagents/settings/pi/extensions/coms.ts \
--coms-name "yoplai-agent" \
--purpose "Provide guidance on Yoplai source code and architecture" \
--project "Orchestrator Extraction"
```

