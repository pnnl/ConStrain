import numpy as np
import pandas as pd
from datetime import timedelta, date
from typing import List, Dict, Union
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import seaborn as sns
import glob, json, os


class CheckLibBase(ABC):
    """Abstract class defining interfaces for item-specific verification classes"""

    points = None
    result = pd.DataFrame()

    def __init__(self, df: pd.DataFrame, params=None, results_folder=None):
        full_df = df.copy(deep=True)
        if params is not None:
            for k, v in params.items():
                full_df[k] = v

        col_list = full_df.columns.values.tolist()
        if not set(self.points_list).issubset(set(col_list)):
            print(f"Dataset is not sufficient for running {self.__class__.__name__}")
            print(set(col_list))
        self.df = full_df[self.points_list]
        self.df.index = pd.to_datetime(self.df.index)
        self.df = self.df.sort_index()
        self.results_folder = results_folder
        self.verify()
        self.result.name = ""

    @property
    def points_list(self) -> List[str]:
        return self.points

    @abstractmethod
    def check_bool(self) -> bool:
        """implementation of the checking boolean return"""
        pass

    @abstractmethod
    def check_detail(self) -> Dict:
        """implementaion of the checking detailed return in Dict"""
        pass

    @abstractmethod
    def verify(self):
        """checking logic implementation, not for user"""
        pass

    @property
    def get_checks(self):
        return self.check_bool(), self.check_detail()

    def add_md(
        self,
        md_file_path,
        img_folder,
        relative_path_to_img_in_md,
        item_dict,
        plot_option=None,
        fig_size=(6.4, 4.8),
    ):
        outcome_bool, outcome_dict = self.get_checks

        img_folder = f"{img_folder}/VerificationCase{item_dict['no']}"
        relative_path_to_img_in_md = (
            f"{relative_path_to_img_in_md}/VerificationCase{item_dict['no']}"
        )
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)

        self.results_folder = img_folder
        if plot_option is None:
            self.plot(plot_option="all-compact", fig_size=fig_size)
            self.plot(plot_option="all-expand", fig_size=fig_size)
            self.plot(plot_option="day-compact", fig_size=fig_size)
            self.plot(plot_option="day-expand", fig_size=fig_size)
        else:
            self.plot(plot_option=plot_option, fig_size=fig_size)
        image_list = glob.glob(f"{img_folder}/*.png")
        image_md_path_list = [
            x.replace(img_folder, relative_path_to_img_in_md) for x in image_list
        ]
        img_md = ""
        for i in range(len(image_list)):
            img_def_path = image_list[i]
            img_rel_path = image_md_path_list[i]
            img_md += f"""
![{img_def_path}]({img_rel_path})
"""

        md_content = f"""
## Results for Verification Case ID {item_dict['no']}

### Pass/Fail check result
{str(outcome_dict)}

### Result visualization
{img_md}

### Verification case definition
```
{json.dumps(item_dict, indent=2)}
```

---

"""
        if md_file_path is not None:
            with open(md_file_path, "a") as fw:
                fw.write(md_content)
        return {
            "md_content": md_content,
            "outcome_notes": outcome_dict,
            "model_file": item_dict["simulation_IO"]["idf"]
            .split("/")[-1]
            .split("\\")[-1]
            .replace(".idf", ""),
            "verification_class": item_dict["verification_class"],
        }

    def plot(self, plot_option, plt_pts=None, fig_size=(6.4, 4.8)):
        """default plot function for showing result"""
        if plt_pts is None:
            plt_pts = self.df.columns.tolist()

        if plot_option is None:
            return

        plot_option = plot_option.strip().lower()
        plt.subplots()
        if plot_option == "all-compact":
            self.all_plot_aio(plt_pts, fig_size)
        elif plot_option == "all-expand":
            self.all_plot_obo(plt_pts, fig_size)
        elif plot_option == "day-compact":
            self.day_plot_aio(plt_pts, fig_size)
        elif plot_option == "day-expand":
            self.day_plot_obo(plt_pts, fig_size)
        else:
            print("Invalid plot option!")
        plt.close("all")
        return

    def all_plot_aio(self, plt_pts, fig_size):
        """All in one plot of all samples"""
        plt.figure(figsize=fig_size)

        # flag
        ax1 = plt.subplot(2, 1, 1)
        sns.scatterplot(x=self.result.index, y=self.result, linewidth=0, s=1)
        plt.xlim([self.df.index[0], self.df.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"All samples Pass / Fail flag plot - {self.__class__.__name__}")

        # datapoints
        ax2 = plt.subplot(2, 1, 2)
        self.df[plt_pts].plot(ax=ax2)
        pt_nan = self.df.isnull().any().to_dict()
        for i, line in enumerate(ax2.get_lines()):
            line_label = line.get_label()
            if pt_nan[line_label]:
                line.set_marker(".")
        ax2.ticklabel_format(useOffset=False, axis="y")

        plt.title(f"All samples data points plot - {self.__class__.__name__}")
        plt.tight_layout()
        plt.savefig(f"{self.results_folder}/All_plot_aio.png")
        print()

    def all_plot_obo(self, plt_pts, fig_size):
        """One by one plot of all samples"""
        num_plots = len(plt_pts) + 1
        plt.figure(figsize=(fig_size[0], fig_size[1] * num_plots))

        # flag
        ax1 = plt.subplot(num_plots, 1, 1)
        sns.scatterplot(x=self.result.index, y=self.result, linewidth=0, s=1)
        plt.xlim([self.df.index[0], self.df.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"All samples Pass / Fail flag plot - {self.__class__.__name__}")

        # datapoints
        pt_nan = self.df.isnull().any().to_dict()
        i = 2
        for pt in plt_pts:
            try:
                axx = plt.subplot(num_plots, 1, i)
                if pt_nan[pt]:
                    self.df[pt].plot(ax=axx, marker=".")
                else:
                    self.df[pt].plot(ax=axx)
                plt.title(f"All samples - {pt} - {self.__class__.__name__}")
                i += 1
                axx.ticklabel_format(useOffset=False, axis="y")
            except:
                print(f"{pt} cannot be plotted by itself, ignored in the plot.")

        plt.tight_layout()
        plt.savefig(f"{self.results_folder}/All_plot_obo.png")
        print()

    def calculate_plot_day(self):
        trueday = None
        truedaydf = None
        falseday = None
        falsedaydf = None
        mixday = None
        mixdaydf = None

        ratio = -0.5

        # Looking for day with most balanced pass/fail samples
        for one_day in self.daterange(
            date(self.df.index[0].year, self.df.index[0].month, self.df.index[0].day),
            date(
                self.df.index[-1].year, self.df.index[-1].month, self.df.index[-1].day
            ),
        ):
            daystr = f"{str(one_day.year)}-{str(one_day.month)}-{str(one_day.day)}"
            daydf = self.df.loc[daystr]
            day = self.result[daystr]
            if (trueday is None) and len(day[day == True]) > 0:
                trueday = day
                truedaydf = daydf
                # print("reach true")
                continue
            if (falseday is None) and len(day[day == False]) > 0:
                falseday = day
                falsedaydf = daydf
                # print("reach false")
                continue

            if len(day[day == False]) == 0 or len(day[day == True]) == 0:
                continue

            new_ratio = len(day[day == True]) / len(day) - 0.5

            if abs(new_ratio) < abs(ratio):
                ratio = new_ratio
                mixday = day
                mixdaydf = daydf

        if mixdaydf is None:
            plotdaydf = daydf
            plotday = day
        else:
            plotdaydf = mixdaydf
            plotday = mixday

        return plotday, plotdaydf

    def day_plot_aio(self, plt_pts, fig_size):
        """ALl in one plot for one day"""
        plt.figure(figsize=fig_size)

        plotday, plotdaydf = self.calculate_plot_day()

        # flag
        ax1 = plt.subplot(2, 1, 1)
        sns.scatterplot(x=plotday.index, y=plotday)
        plt.xlim([plotday.index[0], plotday.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"Example day Pass / Fail flag - {self.__class__.__name__}")

        # datapoints
        ax2 = plt.subplot(2, 1, 2)
        plotdaydf[plt_pts].plot(ax=ax2)
        pt_nan = plotdaydf.isnull().any().to_dict()
        for i, line in enumerate(ax2.get_lines()):
            line_label = line.get_label()
            if pt_nan[line_label]:
                line.set_marker(".")
        ax2.ticklabel_format(useOffset=False, axis="y")

        plt.title(f"Example day data points plot - {self.__class__.__name__}")
        plt.tight_layout()
        plt.savefig(f"{self.results_folder}/Day_plot_aio.png")
        print()

    def day_plot_obo(self, plt_pts, fig_size):
        """One by one plot of all samples"""
        num_plots = len(plt_pts) + 1
        plt.figure(figsize=(fig_size[0], fig_size[1] * num_plots))

        plotday, plotdaydf = self.calculate_plot_day()

        # flag
        ax1 = plt.subplot(num_plots, 1, 1)
        sns.scatterplot(x=plotday.index, y=plotday)
        plt.xlim([plotday.index[0], plotday.index[-1]])
        plt.ylim([-0.2, 1.2])
        plt.title(f"Example day Pass / Fail flag plot - {self.__class__.__name__}")

        # datapoints
        pt_nan = plotdaydf.isnull().any().to_dict()
        i = 2
        for pt in plt_pts:
            try:
                axx = plt.subplot(num_plots, 1, i)
                if pt_nan[pt]:
                    plotdaydf[pt].plot(ax=axx, marker=".")
                else:
                    plotdaydf[pt].plot(ax=axx)
                plt.title(f"Example day - {pt} - {self.__class__.__name__}")
                i += 1
                axx.ticklabel_format(useOffset=False, axis="y")
            except:
                print(f"{pt} cannot be plotted by itself, ignored in the plot.")
        plt.tight_layout()
        plt.savefig(f"{self.results_folder}/Day_plot_obo.png")
        print()

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)


class RuleCheckBase(CheckLibBase):
    def check_bool(self) -> Union[bool, str]:
        if len(self.result[self.result == False] > 0):
            return False
        elif len(self.result[self.result == True] > 0):
            return True
        else:
            return "Untested"

    def check_detail(self) -> Dict:
        output = {
            "Sample #": len(self.result),
            "Pass #": len(self.result[self.result == True]),
            "Fail #": len(self.result[self.result == False]),
            "Verification Passed?": self.check_bool(),
        }

        print("Verification results dict: ")
        print(output)
        return output


from constrain import CheckLibBase, RuleCheckBase


class UserProvidedVerificationItem1(RuleCheckBase):
    points = ["o", "eco_onoff", "m_oa", "m_ea", "tol_o", "tol_m_oa", "tol_m_ea"]

    def automatic_oa_damper_check(self, data):
        if data["o"] < data["tol_o"]:
            if data["eco_onoff"] == 0 and (
                data["m_oa"] >= data["tol_m_oa"] or data["m_ea"] >= data["tol_m_ea"]
            ):
                return False
            else:
                return True
        else:
            return np.nan

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)


class UserProvidedVerificationItem_Beta(RuleCheckBase):
    points = ["o", "eco_onoff", "m_oa", "m_ea", "tol_o", "tol_m_oa", "tol_m_ea"]

    def automatic_oa_damper_check(self, data):
        if data["o"] < data["tol_o"]:
            if data["eco_onoff"] == 0 and (
                data["m_oa"] >= data["tol_m_oa"] or data["m_ea"] >= data["tol_m_ea"]
            ):
                return False
            else:
                return True
        else:
            return np.nan

    def verify(self):
        self.result = self.df.apply(lambda d: self.automatic_oa_damper_check(d), axis=1)
