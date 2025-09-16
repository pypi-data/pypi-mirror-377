import tkinter as tk
import argparse
from tkinter import filedialog, messagebox
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
import rioxarray
from matplotlib.patches import Patch, Polygon
from matplotlib.path import Path
import os
import xarray as xr
import h5netcdf  # Not used directly, but required indirectly
import sys
import re
import subprocess

class GrdViewer(tk.Toplevel):
    def __init__(self, parent, grd_file=None):
        super().__init__(parent)
        self.title("Mean Correlation")
        self.geometry("1500x600")        
        self.data = None
        self.extent = None
        self.ds = None
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.canvas = None
        self.toolbar = None
        self.threshold_var = tk.DoubleVar(self, value=0.1)
        self.entry_thresh = tk.Entry(self, textvariable=self.threshold_var)
        self._syncing = False
        self.mask_poly = None
        self.polygon_patch = None
        self.polygon_coords = []
        self.drawing_polygon = False
        self.filename = None
        self.grd_file = grd_file
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        if self.grd_file:
            self.load_grd_from_path(self.grd_file)

    def on_closing(self):        
        self.destroy()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        if not self.grd_file:
            self.btn_browse = ttk.Button(frm, text="Browse .grd File", command=self.load_grd)
            self.btn_browse.pack(side=tk.LEFT)
            self.lbl_file = ttk.Label(frm, text="No file loaded")
            self.lbl_file.pack(side=tk.LEFT, padx=10)
        else:
            self.lbl_file = ttk.Label(frm, text=self.grd_file)
            self.lbl_file.pack(side=tk.LEFT, padx=10)

        ttk.Label(frm, text="Threshold:").pack(side=tk.LEFT, padx=10)

        vcmd = (self.register(self._validate_float), '%P')
        self.entry_thresh = ttk.Entry(
                frm,
                textvariable=self.threshold_var,
                width=8,
                validate='focusout',
                validatecommand=vcmd
            )
        self.entry_thresh.pack(side=tk.LEFT)

        self.btn_update = ttk.Button(frm, text="Update Mask", command=self.update_mask_with_prompt)
        self.btn_update.pack(side=tk.LEFT, padx=5)

        self.btn_draw_poly = ttk.Button(frm, text="Draw Polygon Mask", command=self.enable_polygon_draw)
        self.btn_draw_poly.pack(side=tk.LEFT, padx=5)

        self.btn_export = ttk.Button(frm, text="Confirm Mask", command=self.export_and_close)
        self.btn_export.pack(side=tk.LEFT, padx=5)

    def _validate_float(self, value):
        if value == "":
            return True
        float_regex = r'^[-+]?(?:\d+\.?\d*|\.\d+)?(?:[eE][-+]?\d+)?$'
        if re.match(float_regex, value) is not None:
            try:
                fval = float(value)
                return 0 <= fval <= 1
            except Exception:
                return False
        return False

    def get_current_threshold(self):
        """Always get the current threshold from the textbox, not from the variable."""
        value = self.entry_thresh.get()
        try:
            thresh = float(value)
            if not (0 <= thresh <= 1):
                raise ValueError
            return thresh
        except Exception:
            messagebox.showerror("Error", "Invalid threshold value. Please enter a number between 0 and 1.")
            return None

    def read_grd_file(self, filename):
        try:
            ds = rioxarray.open_rasterio(filename)
            data = ds.values.squeeze()
            x0, x1 = float(ds.x[0]), float(ds.x[-1])
            y0, y1 = float(ds.y[0]), float(ds.y[-1])
            extent = [min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)]
            return data, extent, ds
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read .grd file:\n{e}")
            return None, None, None

    def get_custom_cmap(self):
        # colors = [
        #     (0.0, "#800000"),
        #     (0.125, "#800000"),
        #     (0.13, "red"),
        #     (0.33, "yellow"),
        #     (0.66, "green"),
        #     (0.79, "blue"),
        #     (0.8, "#191970"),
        #     (1.0, "#191970"),
        # ]
        # Use 4 standard matplotlib colors spread evenly between 0 and 1
        colors = [
            (0.0, "red"),
            (0.33, "yellow"),
            (0.66, "green"),
            (1.0, "blue"),
        ]
        return LinearSegmentedColormap.from_list("custom", colors)

    def load_grd(self):
        filetypes = [("GRD files", "*.grd"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Select .grd file", filetypes=filetypes)
        if not filename:
            return
        self.lbl_file.config(text=filename)
        data, extent, ds = self.read_grd_file(filename)
        if data is not None:
            self.data = data
            self.extent = extent
            self.ds = ds
            self.filename = filename
            self.mask_poly = None
            self.plot_data()

    def load_grd_from_path(self, filename):
        self.lbl_file.config(text=filename)
        data, extent, ds = self.read_grd_file(filename)
        if data is not None:
            self.data = data
            self.extent = extent
            self.ds = ds
            self.filename = filename
            self.mask_poly = None
            self.plot_data()

    # Creates threshold based mask
    def get_threshold_mask(self):
        thresh = self.get_current_threshold()
        if thresh is None:
            return None
        return (self.data < thresh).astype(np.uint8)

    def get_polygon_mask(self):
        if self.mask_poly is not None:
            return self.mask_poly
        else:
            return np.zeros_like(self.data, dtype=np.uint8)

    def get_cumulative_mask(self, use_poly=True):
        mask_thresh = self.get_threshold_mask()
        if mask_thresh is None:
            return None
        if use_poly and self.mask_poly is not None:
            mask_poly = self.get_polygon_mask()
            return np.logical_or(mask_thresh, mask_poly).astype(np.uint8)
        else:
            return mask_thresh

    def update_mask_with_prompt(self):
        if self.data is None or self.extent is None:
            return
        # Always use the current value in the textbox
        thresh = self.get_current_threshold()
        if thresh is None:
            return
        use_poly = True
        if self.mask_poly is not None and np.any(self.mask_poly):
            resp = messagebox.askyesno(
                "Polygon Mask",
                "A polygon mask exists. Do you want to RETAIN it in the new mask?\n"
                "Yes: Retain polygon mask\nNo: Discard polygon mask"
            )
            use_poly = resp
            if not use_poly:
                self.mask_poly = None
        self.plot_data(use_poly=use_poly)

    def plot_data(self, use_poly=True):
        if self.data is None or self.extent is None:
            return

        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()
            self.canvas = None
        if self.toolbar:
            self.toolbar.pack_forget()
            self.toolbar = None

        mask = self.get_cumulative_mask(use_poly=use_poly)
        if mask is None:
            return

        # Flip data and mask vertically for consistent display and export
        data_plot = self.data #np.flipud(self.data)
        mask_plot = mask #np.flipud(mask)
        extent_plot = self.extent

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 5), sharex=True, sharey=True)

        custom_cmap = self.get_custom_cmap()
        im1 = self.ax1.imshow(data_plot, cmap=custom_cmap, vmin=0, vmax=1, origin='lower',
                              aspect='auto', extent=extent_plot)
        cbar1 = self.fig.colorbar(im1, ax=self.ax1, orientation='vertical', fraction=0.046, pad=0.04)
        cbar1.set_label('correlation')
        self.ax1.set_title("Mean Correlation")

        cmap = ListedColormap(['white', 'red'])
        bounds = [-0.5, 0.5, 1.5]
        norm = BoundaryNorm(bounds, cmap.N)
        self.ax2.imshow(mask_plot, cmap=cmap, norm=norm, origin='lower',
                        aspect='auto', extent=extent_plot)
        legend_elements = [Patch(facecolor='red', edgecolor='k', label='Masked values')]
        self.ax2.legend(
            handles=legend_elements,
            loc='center left',
            bbox_to_anchor=(0.75, 1.04),
            borderaxespad=0.,
            frameon=True
        )
        thresh = self.get_current_threshold()
        self.ax2.set_title(f"Mask (thresh={thresh if thresh is not None else '?'})")
        self.ax2.set_xlabel("Range")
        self.ax2.set_ylabel("Azimuth")
        self.ax2.axis('on')

        self.fig.tight_layout()
        self._connect_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(fill=tk.X)
        self.canvas.draw()

    def _connect_axes(self):
        def on_xlim_changed(event_ax):
            if self._syncing:
                return
            self._syncing = True
            try:
                other_ax = self.ax2 if event_ax is self.ax1 else self.ax1
                other_ax.set_xlim(event_ax.get_xlim())
                self.canvas.draw_idle()
            finally:
                self._syncing = False

        def on_ylim_changed(event_ax):
            if self._syncing:
                return
            self._syncing = True
            try:
                other_ax = self.ax2 if event_ax is self.ax1 else self.ax1
                other_ax.set_ylim(event_ax.get_ylim())
                self.canvas.draw_idle()
            finally:
                self._syncing = False

        self.ax1.callbacks.connect('xlim_changed', on_xlim_changed)
        self.ax2.callbacks.connect('xlim_changed', on_xlim_changed)
        self.ax1.callbacks.connect('ylim_changed', on_ylim_changed)
        self.ax2.callbacks.connect('ylim_changed', on_ylim_changed)

    def enable_polygon_draw(self):
        if self.data is None or self.extent is None:
            messagebox.showinfo("Info", "Load a .grd file first.")
            return
        if self.drawing_polygon:
            return
        self.drawing_polygon = True
        self.polygon_coords = []
        if self.polygon_patch:
            self.polygon_patch.remove()
            self.polygon_patch = None
        self.cid_click = self.canvas.mpl_connect('button_press_event', self._on_poly_click)
        self.cid_key = self.canvas.mpl_connect('key_press_event', self._on_poly_key)
        messagebox.showinfo(
            "Polygon Mask",
            "Click on the left plot to add polygon vertices.\n"
            "Right-click or double-click to close polygon.\n"
            "Press 'Esc' to cancel."
        )

    def _on_poly_click(self, event):
        if not self.drawing_polygon or event.inaxes != self.ax1:
            return
        if event.button == 1:  # Left click: add point
            self.polygon_coords.append((event.xdata, event.ydata))
            if self.polygon_patch:
                self.polygon_patch.remove()
            self.polygon_patch = Polygon(self.polygon_coords, closed=False, fill=False, edgecolor='cyan', linewidth=2)
            self.ax1.add_patch(self.polygon_patch)
            self.canvas.draw_idle()
        elif event.button == 3 or event.dblclick:  # Right click or double click: close polygon
            if len(self.polygon_coords) >= 3:
                self._finish_polygon()
            else:
                messagebox.showwarning("Polygon Mask", "Need at least 3 points to close polygon.")

    def _on_poly_key(self, event):
        if not self.drawing_polygon:
            return
        if event.key == 'escape':
            self._cancel_polygon()

    def _finish_polygon(self):
        if self.polygon_patch:
            self.polygon_patch.remove()
        self.polygon_patch = Polygon(self.polygon_coords, closed=True, fill=False, edgecolor='cyan', linewidth=2)
        self.ax1.add_patch(self.polygon_patch)
        self.canvas.draw_idle()
        self.drawing_polygon = False
        confirm = messagebox.askyesno("Polygon Mask", "Apply this polygon as additional mask?")
        if confirm:
            self._apply_polygon_mask()
        else:
            if self.polygon_patch:
                self.polygon_patch.remove()
                self.polygon_patch = None
            self.canvas.draw_idle()

    def _cancel_polygon(self):
        self.drawing_polygon = False
        self.polygon_coords = []
        if self.polygon_patch:
            self.polygon_patch.remove()
            self.polygon_patch = None
        self.canvas.draw_idle()

    def _apply_polygon_mask(self):
        poly = np.array(self.polygon_coords)
        path = Path(poly)
        ny, nx = self.data.shape
        x0, x1, y0, y1 = self.extent
        xs = np.linspace(x0, x1, nx)
        ys = np.linspace(y0, y1, ny)
        xv, yv = np.meshgrid(xs, ys)
        points = np.vstack((xv.flatten(), yv.flatten())).T
        inside = path.contains_points(points).reshape((ny, nx))
        if self.mask_poly is None:
            self.mask_poly = np.zeros_like(self.data, dtype=np.uint8)
        self.mask_poly[inside] = 1
        self.plot_data()

    def save_mask_as_grd(self, ds_in, mask, grd_out):
        # mask_arr = np.where(mask > 0, 1, np.nan).astype(np.float32)
        # if "band" in ds_in.dims:
        #     ds_in = ds_in.squeeze("band", drop=True)
        # mask_da = xr.DataArray(
        #     mask_arr,
        #     dims=ds_in.dims,
        #     coords={k: ds_in.coords[k] for k in ds_in.dims},
        #     attrs=ds_in.attrs,
        # )
        # mask_da.to_netcdf(
        #     grd_out,
        #     engine="h5netcdf",
        #     format="NETCDF4"
        # )
        # import rioxarray
        # # import xarray as xr
        # import numpy as np

        

        # Ensure mask_arr is written with correct x/y coordinates starting at 0
        # Flip mask vertically for consistency with display and export
        mask_arr = np.where(mask > 0, 1, np.nan).astype(np.float32)
        # mask_arr = np.flipud(mask_arr)
        # ny, nx = mask_arr.shape

        # Get x/y from ds_in to ensure same registration as input (GMT gridline registration)
        x = ds_in.x.values
        y = ds_in.y.values

        mask_da = xr.DataArray(
            mask_arr,
            dims=("y", "x"),
            coords={"x": x, "y": y},
            attrs=ds_in.attrs,
            name="z"
        )

        tmp_nc = grd_out.replace(".grd", "_tmp.nc")
        mask_da.to_netcdf(tmp_nc, engine="h5netcdf", format="NETCDF4")

        # Use GMT to convert to classic grd format
        subprocess.run(["gmt", "grdconvert", tmp_nc, f"{grd_out}=nf"], check=True)

        os.remove(tmp_nc)
    def export_and_close(self):
        if self.data is None or self.extent is None or self.ds is None:
            messagebox.showerror("Error", "No data loaded to export.")
            return

        export_dir = os.path.dirname(self.grd_file)
        if not export_dir:
            return

        mask = self.get_cumulative_mask(use_poly=True)
        if mask is None:
            messagebox.showerror("Error", "No mask to export.")
            return

        base = os.path.splitext(os.path.basename(self.filename))[0] if self.filename else "output"
        png1 = os.path.join(export_dir, f"{base}_mean_correlation.png")
        png2 = os.path.join(export_dir, f"{base}_mask.png")
        grd_out = os.path.join(export_dir, "mask_def.grd")

        # Export left plot (mean correlation)
        fig1, ax1 = plt.subplots(figsize=(7, 5))
        custom_cmap = self.get_custom_cmap()
        im1 = ax1.imshow(self.data, cmap=custom_cmap, vmin=0, vmax=1, origin='lower',
                         aspect='auto', extent=self.extent)
        cbar1 = fig1.colorbar(im1, ax=ax1, orientation='vertical', fraction=0.046, pad=0.04)
        cbar1.set_label('correlation')
        ax1.set_title("Mean Correlation")
        ax1.set_xlabel("Range")
        # Export left plot (mean correlation) with vertically flipped data
        fig1, ax1 = plt.subplots(figsize=(7, 5))
        custom_cmap = self.get_custom_cmap()
        data_plot = self.data #np.flipud(self.data)
        im1 = ax1.imshow(data_plot, cmap=custom_cmap, vmin=0, vmax=1, origin='lower',
                         aspect='auto', extent=self.extent)
        cbar1 = fig1.colorbar(im1, ax=ax1, orientation='vertical', fraction=0.046, pad=0.04)
        cbar1.set_label('correlation')
        ax1.set_title("Mean Correlation")
        ax1.set_xlabel("Range")
        ax1.set_ylabel("Azimuth")
        ax1.axis('on')
        fig1.tight_layout()
        fig1.savefig(png1, dpi=300)
        plt.close(fig1)

        # Export middle plot (mask) with vertically flipped mask
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        cmap = ListedColormap(['white', 'red'])
        bounds = [-0.5, 0.5, 1.5]
        norm = BoundaryNorm(bounds, cmap.N)
        mask_plot = mask #np.flipud(mask)
        ax2.imshow(mask_plot, cmap=cmap, norm=norm, origin='lower',
                   aspect='auto', extent=self.extent)
        legend_elements = [Patch(facecolor='red', edgecolor='k', label='Masked values')]
        ax2.legend(
            handles=legend_elements,
            loc='center left',
            bbox_to_anchor=(0.75, 1.04),
            borderaxespad=0.,
            frameon=True
        )
        thresh = self.get_current_threshold()
        ax2.set_title(f"Mask (thresh={thresh if thresh is not None else '?'})")
        ax2.set_xlabel("Range")
        ax2.set_ylabel("Azimuth")
        ax2.axis('on')
        fig2.tight_layout()
        fig2.savefig(png2, dpi=300)
        plt.close(fig2)


        # Handle mask_def.grd file existence
        if os.path.exists(grd_out):
            resp = messagebox.askquestion(
                "mask_def.grd exists",
                "mask_def.grd already exists.\n\n"
                "Overwrite file?\n"
                "Yes: Overwrite\n"
                "No: Rename previous to mask_def.grd.old\n"
                "Cancel: Skip exporting and keep window open",
                icon='warning', type='yesnocancel'
            )
            if resp == 'yes':
                self.save_mask_as_grd(self.ds, mask, grd_out)
            elif resp == 'no':
                old_file = grd_out + ".old"
                try:
                    if os.path.exists(old_file):
                        os.remove(old_file)
                    os.rename(grd_out, old_file)
                    self.save_mask_as_grd(self.ds, mask, grd_out)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename old file:\n{e}")
                    return
            else:  # Cancel
                messagebox.showinfo("Export", "Export skipped. Window remains open.")
                return
        else:
            self.save_mask_as_grd(self.ds, mask, grd_out)

        messagebox.showinfo("Export", f"Exported:\n{png1}\n{png2}\n{grd_out}")
        self.on_closing()


if __name__ == "__main__":    

    parser = argparse.ArgumentParser(description="GMTSAR Mask GUI")
    parser.add_argument("--grd", type=str, help="Full path to input .grd file", default=None)
    args = parser.parse_args()

    app = GrdViewer(grd_file=args.grd)
    app.mainloop()
