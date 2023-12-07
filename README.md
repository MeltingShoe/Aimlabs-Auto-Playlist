# Aimlabs-Auto-Playlist
This program is meant to solve some of the problems I have with the Voltaic benchmarks for aimlabs/kovaaks. It will automatically queue up the next scenario to make sure you focus on your weak points and spend the right amount of time grinding each task.

### TODO:
1. Pull scores and save to file
2. Deeplinks
3. Basically make a normal playlist of benchmarks externally
4. Make auto-benchmark, which scales the amount of times you play each benchmark
5. Do all the complicated stuff to add in fundamental routines
6. Add a UI

### Goals:
- Forces you to take breaks!
- It should effectively combine benchmarks with fundamental routines to target weakpoints.
- It should repeat a task if you score within a percentage of your high score. We never want to stop right after setting a new high score. We want to spend as much time as we can improving, and switch tasks when we stop doing that to be efficient with our time
- Benchmarks should persist between sessions
- Not all benchmarks are done every session.
- For the first session you do all the benchmarks. After that it will only do a few per session.
- Lower ranked categories are benchmarked more often
- Ranks are based on averages
- Energy system works different. It should still make it so that you're not completely stunted by 1 task, but improving at the lower rated task in a subcategory should still improve your rank
- To start we'll just use VT scenarios
- Each task is played a minimum of 2(maybe 3) times.
- After that you need to get within 10% of your highscore to keep going and that threshold tightens every attempt
- It could maybe choose what you need to focus on based off of your average scores, but then pick a specific scenario based on stats like accuracy. So for static dots if your accuracy is above 92% it will give a scenario with big dots but if it's under that it'll go small dots
- The user should be able to pick a length of session when they start in either minutes or number of scenarios
- It will scale the number of different scenarios and the threshold values based on how long the session should be
- It uses deeplinks to launch the scenarios
- It gives instructions like "restart scenario" or "back out to main menu to launch next scenario"
- Deeplinks are launched either by a shortcut or by a timer, not sure which
- It gives guidance on how to do specific tasks like "focus on accuracy" or "stay relaxed" or "try not to lift your mouse"
- The same scenario can have different guidance so we can use the same scenario for working on different things
- Multiple benchmarks can be used for the same category. So rather than doing novice until you've beat it and then moving to intermediate you'll do a combination of both and those scores are like combined somehow
- Eventually I definitely should make custom scenarios for this.
- Every run starts with a warmup, and the difficulty of the warmup changes very quickly(run to run) to make sure to warm up within our skill level
