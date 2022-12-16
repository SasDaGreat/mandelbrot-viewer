# mandelbrot-viewer
A collection of Python programs to graph the Mandelbrot fractal, along with related fractals like Julia sets, Buddhabrots, Newton's fractals etc. It's my longest running singular "project" yet (started in 2018) - project in quotations as it's really just a passion I dip into from time to time. Generating and optimising the generation of fun pictures with maths is fun enough to last months of obsession!

This readme is currently incomplete, but I'll update it with full info on all the programs sometime.



### versions
*Note: version numbers don't really mean recency! It's just to group similar algorithms/purposes together.*
*current most useful versions: v4.(2,3,4), v5.(0,1), v8*


**v1** - initial attempt back in 2018


**v2.1** - zooming in on set enabled, since generation now depends on topleft coordinates of graph. Has a yet untested iterations scaling system - will revamp this using statistics later, to model a curve that will best fit the iterations needed

**2.2** - first time using abs(z) > 2

**2vs2.1** - highlighting differences between v2.1 and v2.2's escape algorithms


**3.1** - attempt at increasing the number of possible colours in the set images (I hadn't discovered fractional iteration yet) by cycling not only H but S and V too; failure coz the images are unappealing


**v4.1** - first usage of fractional iteration algorithm, copied from the internet (first internet help I used)

**v4.1 deformed** - another modification to the iteration equation that produces interesting gifs when iterated

**v4.1 newton's method** - Newton's fractals! Need to manually set the equations and derivates, but works wonders once that's done

**v4.2, non-parallel and parallel** - *(2022)* first time working on this project in 2 years! Preparation for and jump to multiprocessing, with the ability to benchmark between MP and non-MP. Also has a pretty cool inside-set colouring algorithm that I haven't been able to replicate on the higher versions (will try) + tons of other additions like being able to drag and drop a previously-generated v4.2+ image onto a v4.2+ script to generate with those conditions, profiling etc.

**v4.3** - first time jumping into NumPy, after 4 years of meaningless manual Python crunching! Huge speedups, huge Ws

**v4.3 3dplane** - generates a "3D" ndarry by joining together 2D Mandelbrot slices with slightly different conditions each time, like a gif generator (in fact, the saved ndarray files can be used with a gif generator)

**v4.4** - vectorisation of the entire 2D graph instead of singular vertical lines

**v4.3 and v4.4 pan** - most recent update to help in my math class demonstrations, adding the ability to pan and zoom around the graph instead of pressing arrow keys to move

**v4.2 and v4.4 mandeljulia** - realtime Julia set generator/animator! Multiprocessing (v4.4) actually slows the generation down considerably as processes need to start and end on a dime, although v4.4 is more scalable and better for higher resos


**v5** - distance estimator to show actual distance

**v5.1** - same but uses inverse, which is what is used online

**v5.1NEG** - this is the program that produces a pattern I haven't seen before! Uses a negative power on `z`, which only works with distance estimator (v5)

**v5.1 deformed** - same as v4.1 deformed but using distance estimator, new patterns

**julia v5.1D** - failed attempt at using the Decimal module to solve some issues. EXTREMELY slow but does produce interesting patterns! Will use NumPy henceforth to try and increase precision if needed


**v6** - attempt at combining multiple generation techniques into a single colour image. This specific combination looks ugly but I feel there's potential here


**v7** - attempt at recreating a technique seen online (calculating total angle rotated through orbits)

**v7DIS** - same but for Julia


**v8** - Buddhabrot time! Will update this with NumPy soon to increase speeds a hundredfold, since these take time to generate


**v9** - my own colouring algorithm (calculates the last z's angle). Pretty cool but has a stepped effect, wonder if I could remove that with my current expertise?

**v9.1** - also my own (calculates the last z's modulus), even better!


**v10.1** - attempt at another drawing algorithm (drawing lines between orbits), but doesn't really work well. Think this could result in a Buddhabrot-like if done well, which isn't really that novel


**v11** - a friend's idea (calculates the log of the real or imaginary part of last zn)

**v11.1** - modification to friend's idea (calculates the log of the modulus of last zn)



### other scripts
**metadata reader** - reads the PngInfo added to images generated after v4.2

**3d plotter** - plots the 3D arrays saved by v4.3 3dplane... or at least tries to, since those are huge. Wonder how I can get around this limit... Blender?



### gifs
Very incomplete, haven't added most of the gifs I made. Will document these later