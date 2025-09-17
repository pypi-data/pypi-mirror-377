```markdown
# Dead Time Assessment Information

This file contains additional functions and procedures to assess and study the dead time if any change is made in the lidar system or if a long period has passed without the evaluation of this parameter.

The dead time evaluation is based on the method presented by Newsom et al. in the article:
> Newsom, R. K., Turner, D. D., Mielke, B., Clayton, M., Ferrare, R., & Sivaraman, C. (2009). Simultaneous analog and photon counting detection for Raman lidar. Applied Optics, 48(20), 3903–3914. [https://doi.org/10.1364/ao.48.003903](https://doi.org/10.1364/ao.48.003903)

The study of the dead time for a single channel uses all the profiles acquired during a day of measurements, performs a reduction of the dataset through a binning process, and minimizes a cost function based on the differences between `dt_corrected_pc_signal` and analog signal (dc and bz corrected). For every `pc_threshold` used, an optimal dead time is found. However, when the threshold approaches 100 MHz, the non-paralyzable assumption (dead time correction formula) breaks. The optimal tau considered should be one of the results for a threshold below 50 MHz. It can be further compared using a linear fit between the above-mentioned signals looking at the offset, since the relation between the signals should only be proportional. The tau and `pc_threshold` that give a closer to zero offset comprise the optimal value.

The method of studying the optimal tau by varying the `pc_threshold` and then performing the fit is implemented in the `dead_time_assesment_by_channel()`. The necessary functions together with the recently mentioned are in the following file:
- `gfatpy-develop/gfatpy/lidar/quality_assurance/dead_time_assesment.py`

The corresponding test file that performs the whole study and assessment is in:
- `gfatpy-develop/tests/lidar/quality_assurance/test_lidar_deadtime_assesment.py`

However, the data file from the lidar used in the test (2023-02-22) did not have the water vapor channel on. The functions were designed with water vapor signals, so be careful when using other channels except from 408ntx. For other channels like 532nm, we expect other maximums in the raw signal from aerosols or clouds that can affect the `min_corr_range` determination (it was being defined from the max caused by overlap given that water vapor signals are weak and the overlap is an absolute and not a local maximum). For these cases, a short range to calculate correlation is defined (150, 350).
```
